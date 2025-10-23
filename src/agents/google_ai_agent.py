import google.generativeai as genai
from typing import Dict, Any, List
from loguru import logger
import json
from src.collection.wikipedia_collector import WikipediaCollector, CompanyData
from src.preparation.data_preparation import DataPreparationPipeline, ProcessedCompanyData
from src.validation.data_validation import DataValidationPipeline, ValidatedCompanyData
from src.database.connection import db_manager
from src.models.database import Company, Domain, Acquisition, Brand, DataSource, ProcessingStage, ValidationResult as DBValidationResult
from src.config.settings import settings


class GoogleAICompanyDataAgent:
    """Google AI Studio (Gemini) powered agentic AI system for company data collection."""
    
    def __init__(self):
        # Configure Google AI
        if settings.google_ai_api_key:
            genai.configure(api_key=settings.google_ai_api_key)
            self.model = genai.GenerativeModel(settings.google_ai_model)
        else:
            logger.warning("Google AI API key not configured. Please set GOOGLE_AI_API_KEY in .env")
            self.model = None
        
        # Initialize components
        self.collector = WikipediaCollector()
        self.preparation_pipeline = DataPreparationPipeline()
        self.validation_pipeline = DataValidationPipeline()
    
    def process_company(self, company_name: str) -> Dict[str, Any]:
        """Process a company through the complete pipeline using Google AI."""
        logger.info(f"Starting Google AI processing for {company_name}")
        
        if not self.model:
            return {
                'success': False,
                'company_name': company_name,
                'error': 'Google AI API key not configured'
            }
        
        try:
            # Step 1: Collect data
            logger.info("Step 1: Collecting company data from Wikipedia")
            company_data = self.collector.collect_company_data(company_name)
            
            # Step 2: Prepare data
            logger.info("Step 2: Preparing data through 4-stage pipeline")
            processed_data = self.preparation_pipeline.prepare_data(company_data)
            
            # Step 3: Validate data
            logger.info("Step 3: Validating data through 2-stage validation")
            validated_data = self.validation_pipeline.validate_data(processed_data)
            
            # Step 4: AI Analysis and Enhancement
            logger.info("Step 4: AI analysis and enhancement")
            ai_analysis = self._ai_analyze_data(validated_data)
            
            # Step 5: Save to database
            logger.info("Step 5: Saving to database")
            save_result = self._save_to_database(validated_data, ai_analysis)
            
            # Step 6: Generate final report
            logger.info("Step 6: Generating final report")
            final_report = self._generate_final_report(validated_data, ai_analysis)
            
            logger.info(f"Completed Google AI processing for {company_name}")
            return {
                'success': True,
                'company_name': company_name,
                'data_collection': {
                    'company_name': company_data.name,
                    'description': company_data.description,
                    'domains_found': len(company_data.domains),
                    'brands_found': len(company_data.brands),
                    'subsidiaries_found': len(company_data.subsidiaries)
                },
                'data_preparation': {
                    'search_terms': len(processed_data.search_terms),
                    'domains': len(processed_data.domains),
                    'asns': len(processed_data.asns),
                    'netblocks': len(processed_data.netblocks)
                },
                'data_validation': {
                    'overall_score': validated_data.overall_score,
                    'is_valid': validated_data.is_valid,
                    'validation_results': [
                        {
                            'type': result.validation_type,
                            'status': result.status,
                            'score': result.score
                        }
                        for result in validated_data.validation_results
                    ]
                },
                'ai_analysis': ai_analysis,
                'database_save': save_result,
                'final_report': final_report
            }
            
        except Exception as e:
            logger.error(f"Error in Google AI processing for {company_name}: {e}")
            return {
                'success': False,
                'company_name': company_name,
                'error': str(e)
            }
    
    def _ai_analyze_data(self, validated_data: ValidatedCompanyData) -> Dict[str, Any]:
        """Use Google AI to analyze and enhance the collected data."""
        try:
            # Prepare data for AI analysis
            data_summary = {
                'company_name': validated_data.processed_data.name,
                'legal_name': validated_data.processed_data.legal_name,
                'colloquial_name': validated_data.processed_data.colloquial_name,
                'search_terms': list(validated_data.processed_data.search_terms),
                'domains': [d['domain'] for d in validated_data.processed_data.domains],
                'brands': validated_data.processed_data.brands,
                'subsidiaries': validated_data.processed_data.subsidiaries,
                'validation_score': validated_data.overall_score,
                'validation_status': 'passed' if validated_data.is_valid else 'failed'
            }
            
            # Create AI prompt
            prompt = f"""
            You are an expert company data analyst. Analyze the following company data and provide insights:

            Company Data:
            {json.dumps(data_summary, indent=2)}

            Please provide:
            1. Data Quality Assessment (1-100 score)
            2. Missing Information Analysis
            3. Business Intelligence Insights
            4. Recommendations for Data Enhancement
            5. Competitive Analysis (if applicable)
            6. Risk Assessment

            Format your response as a JSON object with the following structure:
            {{
                "data_quality_score": <number>,
                "missing_information": [<list of missing data points>],
                "business_insights": [<list of insights>],
                "recommendations": [<list of recommendations>],
                "competitive_analysis": {{<analysis object>}},
                "risk_assessment": {{<risk analysis object>}},
                "summary": "<overall summary>"
            }}
            """
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            try:
                ai_analysis = json.loads(response.text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                ai_analysis = {
                    "data_quality_score": validated_data.overall_score,
                    "missing_information": ["Unable to parse AI response"],
                    "business_insights": [response.text[:500]],
                    "recommendations": ["Review AI response manually"],
                    "competitive_analysis": {},
                    "risk_assessment": {},
                    "summary": "AI analysis completed with parsing issues"
                }
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "data_quality_score": validated_data.overall_score,
                "missing_information": ["AI analysis failed"],
                "business_insights": ["Error in AI processing"],
                "recommendations": ["Check AI configuration"],
                "competitive_analysis": {},
                "risk_assessment": {},
                "summary": f"AI analysis failed: {str(e)}"
            }
    
    def _save_to_database(self, validated_data: ValidatedCompanyData, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Save validated data and AI analysis to PostgreSQL database."""
        try:
            session = db_manager.get_session()
            
            # Create company record
            company = Company(
                name=validated_data.processed_data.name,
                legal_name=validated_data.processed_data.legal_name,
                colloquial_name=validated_data.processed_data.colloquial_name
            )
            session.add(company)
            session.flush()  # Get the ID
            
            # Save domains
            for domain_info in validated_data.processed_data.domains:
                domain = Domain(
                    company_id=company.id,
                    domain_name=domain_info['domain'],
                    domain_type='primary',
                    asn=domain_info.get('asn'),
                    netblock=domain_info.get('netblock'),
                    is_active=domain_info.get('is_active', False)
                )
                session.add(domain)
            
            # Save acquisitions
            for acquisition_info in validated_data.processed_data.acquisitions:
                acquisition = Acquisition(
                    company_id=company.id,
                    acquired_company_name=acquisition_info.get('acquired_company', ''),
                    acquisition_type=acquisition_info.get('acquisition_type', 'acquisition')
                )
                session.add(acquisition)
            
            # Save brands
            for brand_name in validated_data.processed_data.brands:
                brand = Brand(
                    company_id=company.id,
                    brand_name=brand_name,
                    brand_type='product'
                )
                session.add(brand)
            
            # Save validation results
            for validation_info in validated_data.validation_results:
                validation_result = DBValidationResult(
                    company_id=company.id,
                    validation_type=validation_info.validation_type,
                    validation_status=validation_info.status,
                    validation_score=validation_info.score,
                    validation_details={'recommendations': validation_info.recommendations}
                )
                session.add(validation_result)
            
            # Save AI analysis as data source
            ai_source = DataSource(
                company_id=company.id,
                source_name="Google AI Analysis",
                source_type="ai_analysis",
                source_url="https://aistudio.google.com/",
                raw_data=ai_analysis,
                confidence_score=int(ai_analysis.get('data_quality_score', 0))
            )
            session.add(ai_source)
            
            session.commit()
            session.close()
            
            return {
                'success': True,
                'message': f"Successfully saved data for {company.name} to database",
                'company_id': str(company.id)
            }
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_final_report(self, validated_data: ValidatedCompanyData, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive final report using Google AI."""
        try:
            prompt = f"""
            Generate a comprehensive business intelligence report for {validated_data.processed_data.name} based on the following data:

            Company Information:
            - Name: {validated_data.processed_data.name}
            - Legal Name: {validated_data.processed_data.legal_name}
            - Colloquial Name: {validated_data.processed_data.colloquial_name}
            - Domains: {len(validated_data.processed_data.domains)}
            - Brands: {len(validated_data.processed_data.brands)}
            - Subsidiaries: {len(validated_data.processed_data.subsidiaries)}
            - Validation Score: {validated_data.overall_score}/100

            AI Analysis:
            {json.dumps(ai_analysis, indent=2)}

            Please create a professional business intelligence report with:
            1. Executive Summary
            2. Company Overview
            3. Digital Asset Analysis
            4. Business Intelligence Insights
            5. Recommendations
            6. Risk Assessment
            7. Competitive Positioning

            Format as a structured report with clear sections and actionable insights.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'report': response.text,
                'generated_at': '2024-10-23T15:30:00Z',
                'ai_model': settings.google_ai_model
            }
            
        except Exception as e:
            logger.error(f"Error generating final report: {e}")
            return {
                'success': False,
                'error': str(e),
                'report': 'Failed to generate report'
            }
    
    def process_multiple_companies(self, company_names: List[str]) -> List[Dict[str, Any]]:
        """Process multiple companies using Google AI."""
        results = []
        
        for company_name in company_names:
            result = self.process_company(company_name)
            results.append(result)
        
        return results
    
    def test_google_ai_connection(self) -> Dict[str, Any]:
        """Test Google AI connection and capabilities."""
        try:
            if not self.model:
                return {
                    'success': False,
                    'error': 'Google AI not configured'
                }
            
            # Simple test prompt
            test_prompt = "Hello! Please respond with 'Google AI connection successful' and provide the current date."
            response = self.model.generate_content(test_prompt)
            
            return {
                'success': True,
                'response': response.text,
                'model': settings.google_ai_model,
                'message': 'Google AI connection successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Google AI connection failed'
            }
