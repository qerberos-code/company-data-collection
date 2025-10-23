from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import requests
import socket
import dns.resolver
from urllib.parse import urlparse
import re
from src.preparation.data_preparation import ProcessedCompanyData


@dataclass
class ValidationResult:
    """Result of a validation check."""
    validation_type: str
    status: str  # passed, failed, warning
    score: int  # 1-100
    details: Dict[str, Any]
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class ValidatedCompanyData:
    """Company data after validation."""
    processed_data: ProcessedCompanyData
    validation_results: List[ValidationResult]
    overall_score: float
    is_valid: bool
    final_hierarchy: Dict[str, Any] = None


class DataValidationPipeline:
    """Data validation pipeline with 2 stages as specified."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CompanyDataValidator/1.0'
        })
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 5
    
    def validate_data(self, processed_data: ProcessedCompanyData) -> ValidatedCompanyData:
        """Run the complete data validation pipeline."""
        logger.info(f"Starting data validation for {processed_data.name}")
        
        validation_results = []
        
        # Stage 1: Source - Search terms analyzed and connected to digital assets
        source_result = self._stage1_source_validation(processed_data)
        validation_results.append(source_result)
        
        # Stage 2: Validation - Hierarchy finished for initial research with all terms/assets validated
        validation_result = self._stage2_final_validation(processed_data, validation_results)
        validation_results.append(validation_result)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(validation_results)
        
        # Determine if data is valid
        is_valid = overall_score >= 70 and all(r.status != 'failed' for r in validation_results)
        
        # Create final hierarchy
        final_hierarchy = self._create_final_hierarchy(processed_data, validation_results)
        
        validated_data = ValidatedCompanyData(
            processed_data=processed_data,
            validation_results=validation_results,
            overall_score=overall_score,
            is_valid=is_valid,
            final_hierarchy=final_hierarchy
        )
        
        logger.info(f"Completed data validation for {processed_data.name} - Score: {overall_score:.1f}")
        return validated_data
    
    def _stage1_source_validation(self, data: ProcessedCompanyData) -> ValidationResult:
        """Stage 1: Source - Search terms analyzed and connected to digital assets."""
        logger.info(f"Stage 1: Source validation for {data.name}")
        
        details = {
            'search_terms_validated': 0,
            'domains_verified': 0,
            'asns_verified': 0,
            'netblocks_verified': 0,
            'connections_found': 0,
            'issues': []
        }
        
        # Validate search terms against digital assets
        for search_term in data.search_terms:
            if self._validate_search_term(search_term, data):
                details['search_terms_validated'] += 1
        
        # Verify domains
        for domain_info in data.domains:
            if self._verify_domain(domain_info):
                details['domains_verified'] += 1
        
        # Verify ASNs
        for asn in data.asns:
            if self._verify_asn(asn):
                details['asns_verified'] += 1
        
        # Verify netblocks
        for netblock in data.netblocks:
            if self._verify_netblock(netblock):
                details['netblocks_verified'] += 1
        
        # Find connections between search terms and digital assets
        connections = self._find_term_asset_connections(data)
        details['connections_found'] = len(connections)
        
        # Calculate score
        total_terms = len(data.search_terms)
        total_domains = len(data.domains)
        total_asns = len(data.asns)
        total_netblocks = len(data.netblocks)
        
        if total_terms == 0:
            score = 0
            status = 'failed'
        else:
            validation_rate = (
                details['search_terms_validated'] / total_terms +
                details['domains_verified'] / max(total_domains, 1) +
                details['asns_verified'] / max(total_asns, 1) +
                details['netblocks_verified'] / max(total_netblocks, 1)
            ) / 4 * 100
            
            score = min(100, int(validation_rate))
            status = 'passed' if score >= 80 else 'warning' if score >= 60 else 'failed'
        
        recommendations = self._generate_source_recommendations(details, data)
        
        return ValidationResult(
            validation_type='source',
            status=status,
            score=score,
            details=details,
            recommendations=recommendations
        )
    
    def _stage2_final_validation(self, data: ProcessedCompanyData, previous_results: List[ValidationResult]) -> ValidationResult:
        """Stage 2: Validation - Hierarchy finished for initial research with all terms/assets validated."""
        logger.info(f"Stage 2: Final validation for {data.name}")
        
        details = {
            'hierarchy_completeness': 0,
            'data_consistency': 0,
            'asset_coverage': 0,
            'cross_references': 0,
            'final_issues': []
        }
        
        # Check hierarchy completeness
        hierarchy_score = self._check_hierarchy_completeness(data)
        details['hierarchy_completeness'] = hierarchy_score
        
        # Check data consistency
        consistency_score = self._check_data_consistency(data)
        details['data_consistency'] = consistency_score
        
        # Check asset coverage
        coverage_score = self._check_asset_coverage(data)
        details['asset_coverage'] = coverage_score
        
        # Check cross-references
        cross_ref_score = self._check_cross_references(data)
        details['cross_references'] = cross_ref_score
        
        # Calculate overall score
        overall_score = (hierarchy_score + consistency_score + coverage_score + cross_ref_score) / 4
        
        if overall_score >= 85:
            status = 'passed'
        elif overall_score >= 70:
            status = 'warning'
        else:
            status = 'failed'
        
        recommendations = self._generate_final_recommendations(details, data)
        
        return ValidationResult(
            validation_type='validation',
            status=status,
            score=int(overall_score),
            details=details,
            recommendations=recommendations
        )
    
    def _validate_search_term(self, search_term: str, data: ProcessedCompanyData) -> bool:
        """Validate a search term against available data."""
        # Check if search term appears in company names, brands, or subsidiaries
        term_lower = search_term.lower()
        
        # Check against company names
        if data.name and term_lower in data.name.lower():
            return True
        if data.legal_name and term_lower in data.legal_name.lower():
            return True
        if data.colloquial_name and term_lower in data.colloquial_name.lower():
            return True
        
        # Check against brands
        for brand in data.brands:
            if brand and term_lower in brand.lower():
                return True
        
        # Check against subsidiaries
        for subsidiary in data.subsidiaries:
            if subsidiary and term_lower in subsidiary.lower():
                return True
        
        # Check against domains
        for domain_info in data.domains:
            if term_lower in domain_info['domain'].lower():
                return True
        
        return False
    
    def _verify_domain(self, domain_info: Dict[str, Any]) -> bool:
        """Verify domain information."""
        domain = domain_info['domain']
        
        try:
            # Check DNS resolution
            socket.gethostbyname(domain)
            
            # Check if domain responds to HTTP
            try:
                response = self.session.get(f"http://{domain}", timeout=5)
                return response.status_code < 400
            except:
                return True  # DNS resolves but HTTP might not be available
            
        except socket.gaierror:
            return False
    
    def _verify_asn(self, asn: str) -> bool:
        """Verify ASN information."""
        # This is a simplified verification
        # In practice, you'd use ASN lookup services
        return asn.startswith('AS') and len(asn) > 2
    
    def _verify_netblock(self, netblock: str) -> bool:
        """Verify netblock information."""
        # Check if it's a valid CIDR notation
        try:
            import ipaddress
            ipaddress.ip_network(netblock)
            return True
        except ValueError:
            return False
    
    def _find_term_asset_connections(self, data: ProcessedCompanyData) -> List[Dict[str, Any]]:
        """Find connections between search terms and digital assets."""
        connections = []
        
        for search_term in data.search_terms:
            for domain_info in data.domains:
                if search_term.lower() in domain_info['domain'].lower():
                    connections.append({
                        'term': search_term,
                        'asset_type': 'domain',
                        'asset_value': domain_info['domain'],
                        'connection_strength': 'strong' if search_term.lower() == domain_info['domain'].lower() else 'weak'
                    })
        
        return connections
    
    def _check_hierarchy_completeness(self, data: ProcessedCompanyData) -> int:
        """Check if the company hierarchy is complete."""
        score = 0
        
        # Check if we have basic company information
        if data.name:
            score += 20
        if data.legal_name:
            score += 15
        if data.colloquial_name:
            score += 10
        
        # Check if we have subsidiary information
        if data.subsidiaries:
            score += 20
        
        # Check if we have acquisition information
        if data.acquisitions:
            score += 15
        
        # Check if we have brand information
        if data.brands:
            score += 20
        
        return min(100, score)
    
    def _check_data_consistency(self, data: ProcessedCompanyData) -> int:
        """Check data consistency across different sources."""
        score = 100
        issues = 0
        
        # Check for conflicting information
        if data.name and data.legal_name and data.name.lower() == data.legal_name.lower():
            issues += 1
        
        # Check for duplicate domains
        domains = [d['domain'] for d in data.domains]
        if len(domains) != len(set(domains)):
            issues += 1
        
        # Check for duplicate brands
        if len(data.brands) != len(set(data.brands)):
            issues += 1
        
        # Reduce score based on issues
        score -= issues * 20
        
        return max(0, score)
    
    def _check_asset_coverage(self, data: ProcessedCompanyData) -> int:
        """Check coverage of digital assets."""
        score = 0
        
        # Check domain coverage
        if data.domains:
            active_domains = sum(1 for d in data.domains if d.get('is_active', False))
            if active_domains > 0:
                score += 40
        
        # Check ASN coverage
        if data.asns:
            score += 30
        
        # Check netblock coverage
        if data.netblocks:
            score += 30
        
        return min(100, score)
    
    def _check_cross_references(self, data: ProcessedCompanyData) -> int:
        """Check cross-references between different data elements."""
        score = 0
        
        # Check if search terms cross-reference with domains
        term_domain_matches = 0
        for search_term in data.search_terms:
            for domain_info in data.domains:
                if search_term.lower() in domain_info['domain'].lower():
                    term_domain_matches += 1
                    break
        
        if term_domain_matches > 0:
            score += 50
        
        # Check if brands cross-reference with domains
        brand_domain_matches = 0
        for brand in data.brands:
            for domain_info in data.domains:
                if brand.lower() in domain_info['domain'].lower():
                    brand_domain_matches += 1
                    break
        
        if brand_domain_matches > 0:
            score += 50
        
        return min(100, score)
    
    def _generate_source_recommendations(self, details: Dict[str, Any], data: ProcessedCompanyData) -> List[str]:
        """Generate recommendations based on source validation."""
        recommendations = []
        
        if details['search_terms_validated'] < len(data.search_terms) * 0.8:
            recommendations.append("Consider adding more search terms or improving existing ones")
        
        if details['domains_verified'] < len(data.domains) * 0.8:
            recommendations.append("Verify domain information and check for inactive domains")
        
        if details['connections_found'] < len(data.search_terms) * 0.5:
            recommendations.append("Improve connections between search terms and digital assets")
        
        return recommendations
    
    def _generate_final_recommendations(self, details: Dict[str, Any], data: ProcessedCompanyData) -> List[str]:
        """Generate recommendations based on final validation."""
        recommendations = []
        
        if details['hierarchy_completeness'] < 80:
            recommendations.append("Complete company hierarchy information")
        
        if details['data_consistency'] < 80:
            recommendations.append("Resolve data consistency issues")
        
        if details['asset_coverage'] < 70:
            recommendations.append("Improve digital asset coverage")
        
        if details['cross_references'] < 70:
            recommendations.append("Strengthen cross-references between data elements")
        
        return recommendations
    
    def _calculate_overall_score(self, validation_results: List[ValidationResult]) -> float:
        """Calculate overall validation score."""
        if not validation_results:
            return 0.0
        
        total_score = sum(result.score for result in validation_results)
        return total_score / len(validation_results)
    
    def _create_final_hierarchy(self, data: ProcessedCompanyData, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Create the final validated hierarchy."""
        hierarchy = {
            'company': {
                'name': data.name,
                'legal_name': data.legal_name,
                'colloquial_name': data.colloquial_name,
                'parent_company': data.parent_company
            },
            'subsidiaries': data.subsidiaries,
            'brands': data.brands,
            'acquisitions': data.acquisitions,
            'digital_assets': {
                'domains': data.domains,
                'asns': data.asns,
                'netblocks': data.netblocks
            },
            'search_terms': list(data.search_terms),
            'validation_summary': {
                'overall_score': self._calculate_overall_score(validation_results),
                'validation_results': [
                    {
                        'type': result.validation_type,
                        'status': result.status,
                        'score': result.score
                    }
                    for result in validation_results
                ]
            }
        }
        
        return hierarchy
