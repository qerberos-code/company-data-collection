#!/usr/bin/env python3
"""
Example usage of the Company Data Collection system.
This script demonstrates how to use the system programmatically.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.agents.company_data_agent import CompanyDataAgent
from src.collection.wikipedia_collector import WikipediaCollector
from src.preparation.data_preparation import DataPreparationPipeline
from src.validation.data_validation import DataValidationPipeline
from loguru import logger


def example_basic_usage():
    """Example of basic usage without agentic AI."""
    logger.info("Running basic usage example...")
    
    # Initialize components
    collector = WikipediaCollector()
    preparation_pipeline = DataPreparationPipeline()
    validation_pipeline = DataValidationPipeline()
    
    # Collect data
    company_name = "Alphabet Inc."
    logger.info(f"Collecting data for {company_name}")
    company_data = collector.collect_company_data(company_name)
    
    # Prepare data
    logger.info("Preparing data...")
    processed_data = preparation_pipeline.prepare_data(company_data)
    
    # Validate data
    logger.info("Validating data...")
    validated_data = validation_pipeline.validate_data(processed_data)
    
    # Display results
    logger.info(f"Validation completed. Overall score: {validated_data.overall_score:.1f}")
    logger.info(f"Data is valid: {validated_data.is_valid}")
    
    return validated_data


def example_agentic_usage():
    """Example of agentic AI usage."""
    logger.info("Running agentic AI example...")
    
    # Initialize agent
    agent = CompanyDataAgent()
    
    # Process company
    company_name = "Alphabet Inc."
    result = agent.process_company(company_name)
    
    if result['success']:
        logger.info("Agentic processing completed successfully!")
        logger.info(f"Result: {result['result']}")
    else:
        logger.error(f"Agentic processing failed: {result.get('error', 'Unknown error')}")
    
    return result


def example_multiple_companies():
    """Example of processing multiple companies."""
    logger.info("Running multiple companies example...")
    
    companies = ["Alphabet Inc.", "Microsoft Corporation", "Apple Inc."]
    
    # Initialize agent
    agent = CompanyDataAgent()
    
    # Process multiple companies
    results = agent.process_multiple_companies(companies)
    
    # Display results
    for result in results:
        company_name = result['company_name']
        if result['success']:
            logger.info(f"✅ {company_name}: Success")
        else:
            logger.error(f"❌ {company_name}: Failed - {result.get('error', 'Unknown error')}")
    
    return results


if __name__ == "__main__":
    # Setup basic logging
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    print("Company Data Collection - Example Usage")
    print("=" * 50)
    
    try:
        # Run examples
        print("\n1. Basic Usage Example:")
        basic_result = example_basic_usage()
        
        print("\n2. Agentic AI Example:")
        agentic_result = example_agentic_usage()
        
        print("\n3. Multiple Companies Example:")
        multiple_result = example_multiple_companies()
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        sys.exit(1)
