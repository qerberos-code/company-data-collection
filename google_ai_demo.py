#!/usr/bin/env python3
"""
Google AI Studio Integration Example
Demonstrates how to use Google AI Studio (Gemini) with the company data collection system.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.agents.google_ai_agent import GoogleAICompanyDataAgent
from src.config.settings import settings
from loguru import logger


def main():
    """Main function to demonstrate Google AI integration."""
    print("🤖 Google AI Studio Integration Demo")
    print("=" * 50)
    
    # Check if Google AI API key is configured
    if not settings.google_ai_api_key or settings.google_ai_api_key == "your_google_ai_api_key_here":
        print("❌ Google AI API key not configured!")
        print("\nTo use Google AI Studio:")
        print("1. Go to https://aistudio.google.com/")
        print("2. Get your API key")
        print("3. Update .env file with:")
        print("   GOOGLE_AI_API_KEY=your_actual_api_key_here")
        print("\nAlternatively, you can set it as an environment variable:")
        print("   export GOOGLE_AI_API_KEY=your_actual_api_key_here")
        return
    
    # Initialize Google AI agent
    print(f"🔧 Initializing Google AI agent with model: {settings.google_ai_model}")
    agent = GoogleAICompanyDataAgent()
    
    # Test connection
    print("\n🧪 Testing Google AI connection...")
    test_result = agent.test_google_ai_connection()
    
    if test_result['success']:
        print("✅ Google AI connection successful!")
        print(f"📱 Model: {test_result['model']}")
        print(f"💬 Response: {test_result['response']}")
    else:
        print(f"❌ Google AI connection failed: {test_result['error']}")
        return
    
    # Process a company
    print("\n🏢 Processing company data with Google AI...")
    company_name = "Alphabet Inc."
    
    try:
        result = agent.process_company(company_name)
        
        if result['success']:
            print(f"✅ Successfully processed {company_name}")
            print("\n📊 Results Summary:")
            print(f"   Company: {result['data_collection']['company_name']}")
            print(f"   Domains Found: {result['data_collection']['domains_found']}")
            print(f"   Brands Found: {result['data_collection']['brands_found']}")
            print(f"   Validation Score: {result['data_validation']['overall_score']}")
            
            # Show AI analysis
            ai_analysis = result.get('ai_analysis', {})
            if ai_analysis:
                print(f"\n🤖 AI Analysis:")
                print(f"   Data Quality Score: {ai_analysis.get('data_quality_score', 'N/A')}")
                print(f"   Summary: {ai_analysis.get('summary', 'N/A')[:100]}...")
                
                # Show recommendations
                recommendations = ai_analysis.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 AI Recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"   {i}. {rec}")
            
            # Show final report
            final_report = result.get('final_report', {})
            if final_report.get('success'):
                print(f"\n📋 Final Report Generated:")
                print(f"   Model Used: {final_report.get('ai_model', 'N/A')}")
                print(f"   Report Preview: {final_report.get('report', '')[:200]}...")
            
        else:
            print(f"❌ Failed to process {company_name}: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error processing company: {e}")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    main()
