import pytest
from unittest.mock import Mock, patch
from src.collection.wikipedia_collector import WikipediaCollector, CompanyData
from src.preparation.data_preparation import DataPreparationPipeline, ProcessedCompanyData
from src.validation.data_validation import DataValidationPipeline, ValidatedCompanyData


class TestWikipediaCollector:
    """Test cases for Wikipedia collector."""
    
    def test_company_data_initialization(self):
        """Test CompanyData initialization."""
        data = CompanyData(name="Test Company")
        assert data.name == "Test Company"
        assert data.domains == []
        assert data.acquisitions == []
        assert data.brands == []
        assert data.subsidiaries == []
    
    @patch('wikipedia.page')
    def test_collect_company_data_success(self, mock_page):
        """Test successful company data collection."""
        # Mock Wikipedia page
        mock_page_instance = Mock()
        mock_page_instance.summary = "Test company summary"
        mock_page_instance.content = "Test company content with founded 2020"
        mock_page_instance.links = ["test.com", "example.org"]
        mock_page.return_value = mock_page_instance
        
        collector = WikipediaCollector()
        result = collector.collect_company_data("Test Company")
        
        assert result.name == "Test Company"
        assert result.description == "Test company summary"
        assert isinstance(result.domains, list)
    
    @patch('wikipedia.page')
    def test_collect_company_data_disambiguation(self, mock_page):
        """Test handling of disambiguation errors."""
        from wikipedia.exceptions import DisambiguationError
        
        mock_page.side_effect = DisambiguationError("Test", ["Test Company", "Test Corp"])
        
        collector = WikipediaCollector()
        result = collector.collect_company_data("Test")
        
        # Should return empty CompanyData
        assert result.name == "Test"


class TestDataPreparationPipeline:
    """Test cases for data preparation pipeline."""
    
    def test_processed_company_data_initialization(self):
        """Test ProcessedCompanyData initialization."""
        data = ProcessedCompanyData(name="Test Company")
        assert data.name == "Test Company"
        assert data.search_terms == set()
        assert data.domains == []
        assert data.asns == []
        assert data.netblocks == []
    
    def test_stage1_data_entry(self):
        """Test Stage 1: Data Entry."""
        pipeline = DataPreparationPipeline()
        data = ProcessedCompanyData(
            name="Test Company",
            legal_name="Test Company Inc.",
            brands=["Test Brand"],
            subsidiaries=["Test Subsidiary"]
        )
        
        pipeline._stage1_data_entry(data)
        
        assert len(data.search_terms) > 0
        assert "test company" in data.search_terms
        assert "test company inc." in data.search_terms
        assert "test brand" in data.search_terms
        assert "test subsidiary" in data.search_terms
    
    def test_stage4_enumeration(self):
        """Test Stage 4: Enumeration."""
        pipeline = DataPreparationPipeline()
        data = ProcessedCompanyData(name="Test Company")
        data.search_terms = {"test company"}
        
        pipeline._stage4_enumeration(data)
        
        assert len(data.search_terms) > 1
        assert "test company" in data.search_terms


class TestDataValidationPipeline:
    """Test cases for data validation pipeline."""
    
    def test_validation_result_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(
            validation_type="test",
            status="passed",
            score=85,
            details={"test": "data"}
        )
        
        assert result.validation_type == "test"
        assert result.status == "passed"
        assert result.score == 85
        assert result.details == {"test": "data"}
        assert result.recommendations == []
    
    def test_stage1_source_validation(self):
        """Test Stage 1: Source validation."""
        pipeline = DataValidationPipeline()
        data = ProcessedCompanyData(
            name="Test Company",
            search_terms={"test company", "test"},
            domains=[{"domain": "test.com", "is_active": True}],
            asns=["AS12345"],
            netblocks=["192.168.1.0/24"]
        )
        
        result = pipeline._stage1_source_validation(data)
        
        assert result.validation_type == "source"
        assert result.status in ["passed", "warning", "failed"]
        assert 0 <= result.score <= 100
    
    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        pipeline = DataValidationPipeline()
        
        results = [
            ValidationResult("test1", "passed", 80, {}),
            ValidationResult("test2", "passed", 90, {})
        ]
        
        score = pipeline._calculate_overall_score(results)
        assert score == 85.0


class TestIntegration:
    """Integration tests."""
    
    @patch('wikipedia.page')
    def test_end_to_end_pipeline(self, mock_page):
        """Test complete pipeline from collection to validation."""
        # Mock Wikipedia page
        mock_page_instance = Mock()
        mock_page_instance.summary = "Test company summary"
        mock_page_instance.content = "Test company content"
        mock_page_instance.links = []
        mock_page.return_value = mock_page_instance
        
        # Collection
        collector = WikipediaCollector()
        company_data = collector.collect_company_data("Test Company")
        
        # Preparation
        preparation_pipeline = DataPreparationPipeline()
        processed_data = preparation_pipeline.prepare_data(company_data)
        
        # Validation
        validation_pipeline = DataValidationPipeline()
        validated_data = validation_pipeline.validate_data(processed_data)
        
        # Assertions
        assert validated_data.processed_data.name == "Test Company"
        assert validated_data.overall_score >= 0
        assert validated_data.overall_score <= 100
        assert isinstance(validated_data.is_valid, bool)


if __name__ == "__main__":
    pytest.main([__file__])
