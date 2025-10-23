from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from loguru import logger
import re
import dns.resolver
import socket
from urllib.parse import urlparse
import requests
from src.collection.wikipedia_collector import CompanyData


@dataclass
class ProcessedCompanyData:
    """Enhanced company data after preparation stages."""
    # Basic company information
    name: str
    legal_name: Optional[str] = None
    colloquial_name: Optional[str] = None
    
    # Hierarchical structure
    parent_company: Optional[str] = None
    subsidiaries: List[str] = None
    
    # Search terms for cross-referencing
    search_terms: Set[str] = None
    
    # Domain information
    domains: List[Dict[str, Any]] = None
    asns: List[str] = None
    netblocks: List[str] = None
    
    # Business information
    acquisitions: List[Dict[str, Any]] = None
    brands: List[str] = None
    
    # Metadata
    confidence_scores: Dict[str, float] = None
    
    def __post_init__(self):
        if self.subsidiaries is None:
            self.subsidiaries = []
        if self.search_terms is None:
            self.search_terms = set()
        if self.domains is None:
            self.domains = []
        if self.asns is None:
            self.asns = []
        if self.netblocks is None:
            self.netblocks = []
        if self.acquisitions is None:
            self.acquisitions = []
        if self.brands is None:
            self.brands = []
        if self.confidence_scores is None:
            self.confidence_scores = {}


class DataPreparationPipeline:
    """Data preparation pipeline with 4 stages as specified."""
    
    def __init__(self):
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 5
    
    def prepare_data(self, company_data: CompanyData) -> ProcessedCompanyData:
        """Run the complete data preparation pipeline."""
        logger.info(f"Starting data preparation for {company_data.name}")
        
        # Initialize processed data
        processed_data = ProcessedCompanyData(
            name=company_data.name,
            legal_name=company_data.legal_name,
            colloquial_name=company_data.colloquial_name,
            subsidiaries=company_data.subsidiaries.copy(),
            acquisitions=company_data.acquisitions.copy(),
            brands=company_data.brands.copy()
        )
        
        # Stage 1: Data Entry - General hierarchy with search terms
        self._stage1_data_entry(processed_data)
        
        # Stage 2: Domain Association - Associate domains with logical parents
        self._stage2_domain_association(processed_data)
        
        # Stage 3: DANS Check - Check for digital assets
        self._stage3_dans_check(processed_data)
        
        # Stage 4: Enumeration - All possible representations
        self._stage4_enumeration(processed_data)
        
        logger.info(f"Completed data preparation for {company_data.name}")
        return processed_data
    
    def _stage1_data_entry(self, data: ProcessedCompanyData):
        """Stage 1: General hierarchy with all search terms from data sources and cross-references."""
        logger.info(f"Stage 1: Data Entry for {data.name}")
        
        # Build comprehensive search terms
        search_terms = set()
        
        # Add company names
        if data.name:
            search_terms.add(data.name.lower())
        if data.legal_name:
            search_terms.add(data.legal_name.lower())
        if data.colloquial_name:
            search_terms.add(data.colloquial_name.lower())
        
        # Add brand names
        for brand in data.brands:
            if brand:
                search_terms.add(brand.lower())
        
        # Add subsidiary names
        for subsidiary in data.subsidiaries:
            if subsidiary:
                search_terms.add(subsidiary.lower())
        
        # Add acquisition company names
        for acquisition in data.acquisitions:
            if acquisition.get('acquired_company'):
                search_terms.add(acquisition['acquired_company'].lower())
        
        # Add common variations and abbreviations
        self._add_name_variations(data.name, search_terms)
        
        # Ensure uniqueness
        data.search_terms = search_terms
        
        # Set confidence scores
        data.confidence_scores['data_entry'] = 0.9
        
        logger.info(f"Stage 1 completed: {len(search_terms)} search terms generated")
    
    def _stage2_domain_association(self, data: ProcessedCompanyData):
        """Stage 2: Hierarchy with all domains associated with logical parent, plus additional ASNs/Netblocks."""
        logger.info(f"Stage 2: Domain Association for {data.name}")
        
        # Process existing domains
        enhanced_domains = []
        
        for domain in data.domains:
            if isinstance(domain, str):
                domain_info = self._analyze_domain(domain)
                enhanced_domains.append(domain_info)
            else:
                enhanced_domains.append(domain)
        
        # Find additional domains through search terms
        additional_domains = self._find_additional_domains(data.search_terms)
        
        # Merge and deduplicate
        all_domains = enhanced_domains + additional_domains
        unique_domains = self._deduplicate_domains(all_domains)
        
        data.domains = unique_domains
        
        # Extract ASNs and Netblocks
        for domain_info in data.domains:
            if domain_info.get('asn') and domain_info['asn'] not in data.asns:
                data.asns.append(domain_info['asn'])
            if domain_info.get('netblock') and domain_info['netblock'] not in data.netblocks:
                data.netblocks.append(domain_info['netblock'])
        
        data.confidence_scores['domain_association'] = 0.8
        
        logger.info(f"Stage 2 completed: {len(data.domains)} domains, {len(data.asns)} ASNs, {len(data.netblocks)} netblocks")
    
    def _stage3_dans_check(self, data: ProcessedCompanyData):
        """Stage 3: Domain, ASN, Netblocks (DANS) Check - Check for digital assets that may have been missed."""
        logger.info(f"Stage 3: DANS Check for {data.name}")
        
        # Check each search term for potential digital assets
        additional_assets = []
        
        for search_term in data.search_terms:
            # Check for potential domains
            potential_domains = self._check_search_term_for_domains(search_term)
            additional_assets.extend(potential_domains)
            
            # Check for ASN information
            asn_info = self._check_search_term_for_asn(search_term)
            if asn_info:
                additional_assets.append(asn_info)
        
        # Merge with existing data
        for asset in additional_assets:
            if asset.get('type') == 'domain':
                domain_info = self._analyze_domain(asset['value'])
                if domain_info not in data.domains:
                    data.domains.append(domain_info)
            elif asset.get('type') == 'asn' and asset['value'] not in data.asns:
                data.asns.append(asset['value'])
        
        data.confidence_scores['dans_check'] = 0.7
        
        logger.info(f"Stage 3 completed: Found {len(additional_assets)} additional digital assets")
    
    def _stage4_enumeration(self, data: ProcessedCompanyData):
        """Stage 4: Enumeration - Hierarchy with all possible representations of company names."""
        logger.info(f"Stage 4: Enumeration for {data.name}")
        
        # Generate all possible representations
        all_representations = set()
        
        # Add existing search terms
        all_representations.update(data.search_terms)
        
        # Generate variations for each name
        for name in [data.name, data.legal_name, data.colloquial_name]:
            if name:
                variations = self._generate_name_variations(name)
                all_representations.update(variations)
        
        # Generate variations for brands and subsidiaries
        for brand in data.brands:
            if brand:
                variations = self._generate_name_variations(brand)
                all_representations.update(variations)
        
        for subsidiary in data.subsidiaries:
            if subsidiary:
                variations = self._generate_name_variations(subsidiary)
                all_representations.update(variations)
        
        # Update search terms with all representations
        data.search_terms = all_representations
        
        data.confidence_scores['enumeration'] = 0.85
        
        logger.info(f"Stage 4 completed: {len(all_representations)} total representations generated")
    
    def _add_name_variations(self, name: str, search_terms: Set[str]):
        """Add common variations of a company name."""
        if not name:
            return
        
        name_lower = name.lower()
        
        # Add the name itself
        search_terms.add(name_lower)
        
        # Add without common suffixes
        suffixes = ['inc', 'inc.', 'llc', 'corp', 'corporation', 'ltd', 'limited', 'co', 'company']
        for suffix in suffixes:
            if name_lower.endswith(f' {suffix}'):
                base_name = name_lower[:-len(f' {suffix}')].strip()
                search_terms.add(base_name)
        
        # Add with different suffixes
        for suffix in suffixes:
            if not name_lower.endswith(suffix):
                search_terms.add(f"{name_lower} {suffix}")
    
    def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze a domain for additional information."""
        domain_info = {
            'domain': domain,
            'is_active': False,
            'asn': None,
            'netblock': None,
            'ip_address': None
        }
        
        try:
            # Check if domain resolves
            ip_addresses = socket.gethostbyname_ex(domain)[2]
            if ip_addresses:
                domain_info['is_active'] = True
                domain_info['ip_address'] = ip_addresses[0]  # Primary IP
                
                # Try to get ASN information (simplified)
                # In a real implementation, you'd use services like IPInfo or similar
                domain_info['asn'] = f"AS{hash(ip_addresses[0]) % 100000}"  # Mock ASN
                domain_info['netblock'] = f"{ip_addresses[0]}/24"  # Mock netblock
                
        except socket.gaierror:
            domain_info['is_active'] = False
        
        return domain_info
    
    def _find_additional_domains(self, search_terms: Set[str]) -> List[Dict[str, Any]]:
        """Find additional domains based on search terms."""
        additional_domains = []
        
        for term in search_terms:
            # Generate potential domain names
            potential_domains = [
                f"{term}.com",
                f"{term}.org",
                f"{term}.net",
                f"{term}.io",
                f"{term}.co"
            ]
            
            for domain in potential_domains:
                domain_info = self._analyze_domain(domain)
                if domain_info['is_active']:
                    additional_domains.append(domain_info)
        
        return additional_domains
    
    def _deduplicate_domains(self, domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate domains."""
        seen = set()
        unique_domains = []
        
        for domain_info in domains:
            domain = domain_info['domain']
            if domain not in seen:
                seen.add(domain)
                unique_domains.append(domain_info)
        
        return unique_domains
    
    def _check_search_term_for_domains(self, search_term: str) -> List[Dict[str, Any]]:
        """Check if a search term corresponds to any domains."""
        # This is a simplified implementation
        # In practice, you'd use domain discovery tools
        return []
    
    def _check_search_term_for_asn(self, search_term: str) -> Optional[Dict[str, Any]]:
        """Check if a search term corresponds to any ASN information."""
        # This is a simplified implementation
        # In practice, you'd use ASN lookup services
        return None
    
    def _generate_name_variations(self, name: str) -> Set[str]:
        """Generate all possible variations of a name."""
        variations = set()
        
        if not name:
            return variations
        
        name_lower = name.lower()
        variations.add(name_lower)
        
        # Remove punctuation
        clean_name = re.sub(r'[^\w\s]', '', name_lower)
        variations.add(clean_name)
        
        # Split into words and create combinations
        words = clean_name.split()
        if len(words) > 1:
            # Add individual words
            for word in words:
                variations.add(word)
            
            # Add combinations
            variations.add(' '.join(words))
            variations.add(''.join(words))
        
        return variations
