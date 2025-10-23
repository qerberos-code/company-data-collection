import wikipedia
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
import time
import json
from src.config.settings import settings


@dataclass
class CompanyData:
    """Structured company data container."""
    name: str
    legal_name: Optional[str] = None
    colloquial_name: Optional[str] = None
    domains: List[str] = None
    acquisitions: List[Dict[str, Any]] = None
    brands: List[str] = None
    subsidiaries: List[str] = None
    description: Optional[str] = None
    founded_date: Optional[str] = None
    headquarters: Optional[str] = None
    ceo: Optional[str] = None
    revenue: Optional[str] = None
    employees: Optional[str] = None
    
    def __post_init__(self):
        if self.domains is None:
            self.domains = []
        if self.acquisitions is None:
            self.acquisitions = []
        if self.brands is None:
            self.brands = []
        if self.subsidiaries is None:
            self.subsidiaries = []


class WikipediaCollector:
    """Wikipedia data collector for company information."""
    
    def __init__(self):
        wikipedia.set_user_agent(settings.wikipedia_user_agent)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.wikipedia_user_agent
        })
    
    def collect_company_data(self, company_name: str) -> CompanyData:
        """Collect comprehensive company data from Wikipedia."""
        logger.info(f"Starting data collection for {company_name}")
        
        try:
            # Get Wikipedia page
            page = wikipedia.page(company_name)
            
            # Extract basic information
            company_data = CompanyData(name=company_name)
            company_data.description = page.summary
            
            # Parse the full content for detailed information
            self._parse_wikipedia_content(page.content, company_data)
            
            # Get additional pages for subsidiaries and acquisitions
            self._collect_related_entities(page, company_data)
            
            logger.info(f"Successfully collected data for {company_name}")
            return company_data
            
        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Disambiguation error for {company_name}: {e}")
            # Try the first option
            if e.options:
                return self.collect_company_data(e.options[0])
        except wikipedia.exceptions.PageError:
            logger.error(f"Page not found for {company_name}")
            return CompanyData(name=company_name)
        except Exception as e:
            logger.error(f"Error collecting data for {company_name}: {e}")
            return CompanyData(name=company_name)
    
    def _parse_wikipedia_content(self, content: str, company_data: CompanyData):
        """Parse Wikipedia content to extract structured data."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Extract legal name
            if 'legal name' in line.lower() or 'incorporated as' in line.lower():
                company_data.legal_name = self._extract_value(line)
            
            # Extract colloquial name
            if 'commonly known as' in line.lower() or 'colloquially' in line.lower():
                company_data.colloquial_name = self._extract_value(line)
            
            # Extract founded date
            if 'founded' in line.lower() and not company_data.founded_date:
                company_data.founded_date = self._extract_value(line)
            
            # Extract headquarters
            if 'headquarters' in line.lower() and not company_data.headquarters:
                company_data.headquarters = self._extract_value(line)
            
            # Extract CEO
            if 'ceo' in line.lower() and not company_data.ceo:
                company_data.ceo = self._extract_value(line)
            
            # Extract revenue
            if 'revenue' in line.lower() and not company_data.revenue:
                company_data.revenue = self._extract_value(line)
            
            # Extract employee count
            if 'employees' in line.lower() and not company_data.employees:
                company_data.employees = self._extract_value(line)
            
            # Extract domains (look for website mentions)
            if 'website' in line.lower() or 'domain' in line.lower():
                domain = self._extract_domain(line)
                if domain and domain not in company_data.domains:
                    company_data.domains.append(domain)
            
            # Extract acquisitions
            if 'acquired' in line.lower() or 'acquisition' in line.lower():
                acquisition = self._extract_acquisition(line)
                if acquisition:
                    company_data.acquisitions.append(acquisition)
            
            # Extract brands/products
            if 'brand' in line.lower() or 'product' in line.lower():
                brand = self._extract_brand(line)
                if brand and brand not in company_data.brands:
                    company_data.brands.append(brand)
    
    def _extract_value(self, line: str) -> Optional[str]:
        """Extract value from a Wikipedia line."""
        # Simple extraction - look for content after colons or common patterns
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                value = parts[1].strip()
                # Clean up the value
                value = value.replace('[[', '').replace(']]', '')
                value = value.split('|')[0]  # Remove pipe notation
                return value.strip()
        return None
    
    def _extract_domain(self, line: str) -> Optional[str]:
        """Extract domain name from a line."""
        import re
        # Look for common domain patterns
        domain_pattern = r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(domain_pattern, line)
        if match:
            return match.group(1)
        
        # Look for domain-like patterns without protocol
        domain_pattern = r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(domain_pattern, line)
        if match and 'wikipedia' not in match.group(1).lower():
            return match.group(1)
        
        return None
    
    def _extract_acquisition(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract acquisition information from a line."""
        # This is a simplified extraction - in practice, you'd want more sophisticated parsing
        if 'acquired' in line.lower():
            return {
                'acquired_company': self._extract_value(line),
                'acquisition_date': None,  # Would need more sophisticated parsing
                'acquisition_value': None,
                'source': 'wikipedia'
            }
        return None
    
    def _extract_brand(self, line: str) -> Optional[str]:
        """Extract brand/product name from a line."""
        # Simple brand extraction
        if 'brand' in line.lower() or 'product' in line.lower():
            return self._extract_value(line)
        return None
    
    def _collect_related_entities(self, page: wikipedia.WikipediaPage, company_data: CompanyData):
        """Collect information about subsidiaries and related entities."""
        try:
            # Look for subsidiary information in the content
            content_lower = page.content.lower()
            
            # Extract subsidiaries mentioned in the content
            if 'subsidiary' in content_lower or 'subsidiaries' in content_lower:
                # This would need more sophisticated parsing in a real implementation
                pass
            
            # Extract more domains from external links
            if hasattr(page, 'links'):
                for link in page.links:
                    if self._is_domain_link(link):
                        domain = self._extract_domain(link)
                        if domain and domain not in company_data.domains:
                            company_data.domains.append(domain)
            
        except Exception as e:
            logger.warning(f"Error collecting related entities: {e}")
    
    def _is_domain_link(self, link: str) -> bool:
        """Check if a link looks like a domain."""
        return '.' in link and any(tld in link.lower() for tld in ['.com', '.org', '.net', '.io', '.co'])
    
    def collect_multiple_companies(self, company_names: List[str]) -> List[CompanyData]:
        """Collect data for multiple companies."""
        results = []
        
        for name in company_names:
            logger.info(f"Collecting data for {name}")
            try:
                data = self.collect_company_data(name)
                results.append(data)
                
                # Add delay to be respectful to Wikipedia
                time.sleep(settings.request_delay)
                
            except Exception as e:
                logger.error(f"Failed to collect data for {name}: {e}")
                results.append(CompanyData(name=name))
        
        return results
    
    def save_raw_data(self, company_data: CompanyData, source_url: str) -> Dict[str, Any]:
        """Save raw collected data in JSON format."""
        raw_data = {
            'company_name': company_data.name,
            'legal_name': company_data.legal_name,
            'colloquial_name': company_data.colloquial_name,
            'domains': company_data.domains,
            'acquisitions': company_data.acquisitions,
            'brands': company_data.brands,
            'subsidiaries': company_data.subsidiaries,
            'description': company_data.description,
            'founded_date': company_data.founded_date,
            'headquarters': company_data.headquarters,
            'ceo': company_data.ceo,
            'revenue': company_data.revenue,
            'employees': company_data.employees,
            'source_url': source_url,
            'collected_at': time.time()
        }
        
        return raw_data
