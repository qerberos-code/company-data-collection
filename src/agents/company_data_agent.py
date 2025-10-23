from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Any, List
from loguru import logger
import json
from src.collection.wikipedia_collector import WikipediaCollector, CompanyData
from src.preparation.data_preparation import DataPreparationPipeline, ProcessedCompanyData
from src.validation.data_validation import DataValidationPipeline, ValidatedCompanyData
from src.database.connection import db_manager
from src.models.database import Company, Domain, Acquisition, Brand, DataSource, ProcessingStage, ValidationResult as DBValidationResult
from src.config.settings import settings


class CompanyDataAgent:
    """Agentic AI system for company data collection, preparation, and validation."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=settings.openai_api_key
        )
        
        # Initialize components
        self.collector = WikipediaCollector()
        self.preparation_pipeline = DataPreparationPipeline()
        self.validation_pipeline = DataValidationPipeline()
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agentic AI system."""
        
        def collect_company_data(company_name: str) -> str:
            """Collect company data from Wikipedia."""
            try:
                data = self.collector.collect_company_data(company_name)
                return json.dumps({
                    'name': data.name,
                    'legal_name': data.legal_name,
                    'colloquial_name': data.colloquial_name,
                    'domains': data.domains,
                    'acquisitions': data.acquisitions,
                    'brands': data.brands,
                    'subsidiaries': data.subsidiaries,
                    'description': data.description
                }, indent=2)
            except Exception as e:
                return f"Error collecting data: {str(e)}"
        
        def prepare_data(raw_data_json: str) -> str:
            """Prepare and enhance collected data."""
            try:
                raw_data = json.loads(raw_data_json)
                company_data = CompanyData(
                    name=raw_data['name'],
                    legal_name=raw_data.get('legal_name'),
                    colloquial_name=raw_data.get('colloquial_name'),
                    domains=raw_data.get('domains', []),
                    acquisitions=raw_data.get('acquisitions', []),
                    brands=raw_data.get('brands', []),
                    subsidiaries=raw_data.get('subsidiaries', [])
                )
                
                processed_data = self.preparation_pipeline.prepare_data(company_data)
                return json.dumps({
                    'name': processed_data.name,
                    'legal_name': processed_data.legal_name,
                    'colloquial_name': processed_data.colloquial_name,
                    'search_terms': list(processed_data.search_terms),
                    'domains': processed_data.domains,
                    'asns': processed_data.asns,
                    'netblocks': processed_data.netblocks,
                    'acquisitions': processed_data.acquisitions,
                    'brands': processed_data.brands,
                    'subsidiaries': processed_data.subsidiaries,
                    'confidence_scores': processed_data.confidence_scores
                }, indent=2)
            except Exception as e:
                return f"Error preparing data: {str(e)}"
        
        def validate_data(processed_data_json: str) -> str:
            """Validate prepared data."""
            try:
                processed_data_dict = json.loads(processed_data_json)
                processed_data = ProcessedCompanyData(
                    name=processed_data_dict['name'],
                    legal_name=processed_data_dict.get('legal_name'),
                    colloquial_name=processed_data_dict.get('colloquial_name'),
                    search_terms=set(processed_data_dict.get('search_terms', [])),
                    domains=processed_data_dict.get('domains', []),
                    asns=processed_data_dict.get('asns', []),
                    netblocks=processed_data_dict.get('netblocks', []),
                    acquisitions=processed_data_dict.get('acquisitions', []),
                    brands=processed_data_dict.get('brands', []),
                    subsidiaries=processed_data_dict.get('subsidiaries', []),
                    confidence_scores=processed_data_dict.get('confidence_scores', {})
                )
                
                validated_data = self.validation_pipeline.validate_data(processed_data)
                return json.dumps({
                    'is_valid': validated_data.is_valid,
                    'overall_score': validated_data.overall_score,
                    'validation_results': [
                        {
                            'type': result.validation_type,
                            'status': result.status,
                            'score': result.score,
                            'recommendations': result.recommendations
                        }
                        for result in validated_data.validation_results
                    ],
                    'final_hierarchy': validated_data.final_hierarchy
                }, indent=2)
            except Exception as e:
                return f"Error validating data: {str(e)}"
        
        def save_to_database(validated_data_json: str) -> str:
            """Save validated data to PostgreSQL database."""
            try:
                validated_data_dict = json.loads(validated_data_json)
                hierarchy = validated_data_dict['final_hierarchy']
                
                # Save to database
                session = db_manager.get_session()
                
                # Create company record
                company = Company(
                    name=hierarchy['company']['name'],
                    legal_name=hierarchy['company']['legal_name'],
                    colloquial_name=hierarchy['company']['colloquial_name']
                )
                session.add(company)
                session.flush()  # Get the ID
                
                # Save domains
                for domain_info in hierarchy['digital_assets']['domains']:
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
                for acquisition_info in hierarchy['acquisitions']:
                    acquisition = Acquisition(
                        company_id=company.id,
                        acquired_company_name=acquisition_info.get('acquired_company', ''),
                        acquisition_type=acquisition_info.get('acquisition_type', 'acquisition')
                    )
                    session.add(acquisition)
                
                # Save brands
                for brand_name in hierarchy['brands']:
                    brand = Brand(
                        company_id=company.id,
                        brand_name=brand_name,
                        brand_type='product'
                    )
                    session.add(brand)
                
                # Save validation results
                for validation_info in validated_data_dict['validation_results']:
                    validation_result = DBValidationResult(
                        company_id=company.id,
                        validation_type=validation_info['type'],
                        validation_status=validation_info['status'],
                        validation_score=validation_info['score'],
                        validation_details={'recommendations': validation_info['recommendations']}
                    )
                    session.add(validation_result)
                
                session.commit()
                session.close()
                
                return f"Successfully saved data for {company.name} to database"
                
            except Exception as e:
                return f"Error saving to database: {str(e)}"
        
        def analyze_results(results_json: str) -> str:
            """Analyze and provide insights on the collected data."""
            try:
                results = json.loads(results_json)
                
                analysis = {
                    'summary': f"Data collection completed for {results.get('company_name', 'Unknown')}",
                    'data_quality': f"Overall validation score: {results.get('overall_score', 0):.1f}/100",
                    'recommendations': [],
                    'next_steps': []
                }
                
                # Analyze validation results
                validation_results = results.get('validation_results', [])
                for result in validation_results:
                    if result['status'] == 'failed':
                        analysis['recommendations'].append(f"Fix {result['type']} validation issues")
                    elif result['status'] == 'warning':
                        analysis['recommendations'].append(f"Review {result['type']} validation warnings")
                
                # Suggest next steps
                if results.get('overall_score', 0) >= 80:
                    analysis['next_steps'].append("Data quality is good - proceed with analysis")
                else:
                    analysis['next_steps'].append("Improve data quality before proceeding")
                
                return json.dumps(analysis, indent=2)
                
            except Exception as e:
                return f"Error analyzing results: {str(e)}"
        
        return [
            Tool(
                name="collect_company_data",
                description="Collect company data from Wikipedia. Input: company name (string)",
                func=collect_company_data
            ),
            Tool(
                name="prepare_data",
                description="Prepare and enhance collected data through 4-stage pipeline. Input: raw data JSON",
                func=prepare_data
            ),
            Tool(
                name="validate_data",
                description="Validate prepared data through 2-stage validation. Input: processed data JSON",
                func=validate_data
            ),
            Tool(
                name="save_to_database",
                description="Save validated data to PostgreSQL database. Input: validated data JSON",
                func=save_to_database
            ),
            Tool(
                name="analyze_results",
                description="Analyze collected data and provide insights. Input: results JSON",
                func=analyze_results
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agentic AI agent."""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert company data analyst specializing in collecting, preparing, and validating corporate information. 

Your task is to:
1. Collect comprehensive company data from Wikipedia
2. Prepare the data through a 4-stage pipeline (Data Entry, Domain Association, DANS Check, Enumeration)
3. Validate the data through a 2-stage process (Source validation, Final validation)
4. Save the results to a PostgreSQL database
5. Provide analysis and recommendations

For Alphabet Inc. (Google's parent company), focus on collecting:
- Company names (legal, colloquial)
- Domain names of acquisitions, brands, mergers
- Subsidiary hierarchy
- Digital assets (ASNs, netblocks)

Always use the tools in sequence and provide detailed analysis of each step."""),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True
        )
    
    def process_company(self, company_name: str) -> Dict[str, Any]:
        """Process a company through the complete pipeline."""
        logger.info(f"Starting agentic processing for {company_name}")
        
        try:
            # Run the agent
            result = self.agent.invoke({
                "input": f"Process company data for {company_name}. Collect data from Wikipedia, prepare it through the 4-stage pipeline, validate it through the 2-stage validation, save to database, and provide analysis."
            })
            
            logger.info(f"Completed agentic processing for {company_name}")
            return {
                'success': True,
                'company_name': company_name,
                'result': result['output'],
                'intermediate_steps': result.get('intermediate_steps', [])
            }
            
        except Exception as e:
            logger.error(f"Error in agentic processing for {company_name}: {e}")
            return {
                'success': False,
                'company_name': company_name,
                'error': str(e)
            }
    
    def process_multiple_companies(self, company_names: List[str]) -> List[Dict[str, Any]]:
        """Process multiple companies."""
        results = []
        
        for company_name in company_names:
            result = self.process_company(company_name)
            results.append(result)
        
        return results
