# Company Data Collection Prototype - Project Summary

## 🎯 Project Overview

This is a comprehensive **agentic AI prototype** for company data collection, preparation, and validation, specifically designed to collect information about **Alphabet Holdings** (Google's parent company) from Wikipedia and process it through a sophisticated pipeline.

## 🏗️ Architecture

### Core Components

1. **Data Collection** (`src/collection/`)
   - Wikipedia data extraction
   - Company information parsing
   - Domain and acquisition discovery

2. **Data Preparation** (`src/preparation/`)
   - **4-Stage Pipeline**:
     - Stage 1: Data Entry (hierarchy with search terms)
     - Stage 2: Domain Association (domains + ASNs/Netblocks)
     - Stage 3: DANS Check (digital asset verification)
     - Stage 4: Enumeration (all name representations)

3. **Data Validation** (`src/validation/`)
   - **2-Stage Validation**:
     - Stage 1: Source validation (search terms → digital assets)
     - Stage 2: Final validation (hierarchy completeness)

4. **Agentic AI** (`src/agents/`)
   - LangChain-powered orchestration
   - Intelligent tool selection
   - Automated pipeline execution

5. **Database Storage** (`src/database/`, `src/models/`)
   - PostgreSQL integration
   - Comprehensive schema design
   - JSON data storage

## 📊 Data Schema

### Core Tables
- **Companies**: Main entity with legal/colloquial names
- **Domains**: Domain names with ASN/Netblock info
- **Acquisitions**: Company acquisitions and mergers
- **Brands**: Company brands and products
- **Data Sources**: Source tracking and raw data
- **Processing Stages**: Pipeline stage monitoring
- **Validation Results**: Quality assurance results

## 🚀 Key Features

### Data Collection
- ✅ Wikipedia API integration
- ✅ Company hierarchy extraction
- ✅ Domain name discovery
- ✅ Acquisition tracking
- ✅ Brand identification

### Data Preparation
- ✅ Search term generation
- ✅ Domain analysis and verification
- ✅ ASN/Netblock discovery
- ✅ Name variation enumeration
- ✅ Cross-reference validation

### Data Validation
- ✅ Source verification
- ✅ Digital asset validation
- ✅ Hierarchy completeness
- ✅ Data consistency checks
- ✅ Quality scoring (1-100)

### Agentic AI
- ✅ LangChain integration
- ✅ OpenAI GPT-4 powered
- ✅ Tool-based architecture
- ✅ Automated orchestration
- ✅ Intelligent decision making

## 📁 Project Structure

```
datacollection/
├── src/
│   ├── agents/           # Agentic AI components
│   ├── collection/       # Data collection modules
│   ├── preparation/      # Data preparation pipeline
│   ├── validation/       # Data validation pipeline
│   ├── database/         # Database connection
│   ├── models/          # Database models
│   └── config/          # Configuration
├── tests/               # Test suite
├── logs/               # Log files
├── data/               # Data storage
├── main.py             # Main orchestration script
├── example.py          # Usage examples
├── requirements.txt    # Dependencies
├── setup.py           # Package setup
├── README.md          # Documentation
└── config.env.example # Configuration template
```

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.11+**: Main programming language
- **LangChain**: Agentic AI framework
- **OpenAI GPT-4**: Language model
- **PostgreSQL**: Database storage
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation

### Data Processing
- **Wikipedia API**: Data source
- **BeautifulSoup**: HTML parsing
- **Requests**: HTTP client
- **DNS Python**: Domain resolution
- **Pandas**: Data manipulation

### Development Tools
- **Pytest**: Testing framework
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Rich**: Terminal output
- **Loguru**: Logging

## 🎯 Use Case: Alphabet Holdings

### Target Data Collection
- **Company Names**: Alphabet Inc., Google LLC
- **Legal Names**: Alphabet Inc., Google LLC
- **Colloquial Names**: Google, Alphabet
- **Domains**: google.com, alphabet.com, youtube.com, etc.
- **Acquisitions**: YouTube, Android, DeepMind, etc.
- **Brands**: Google, YouTube, Android, Chrome, Gmail, etc.
- **Subsidiaries**: Google LLC, YouTube LLC, Waymo, etc.

### Expected Output
```json
{
  "company": {
    "name": "Alphabet Inc.",
    "legal_name": "Alphabet Inc.",
    "colloquial_name": "Google"
  },
  "subsidiaries": ["Google LLC", "YouTube", "Waymo", "DeepMind"],
  "brands": ["Google", "YouTube", "Android", "Chrome", "Gmail"],
  "digital_assets": {
    "domains": [
      {"domain": "google.com", "is_active": true, "asn": "AS15169"},
      {"domain": "youtube.com", "is_active": true, "asn": "AS15169"}
    ],
    "asns": ["AS15169"],
    "netblocks": ["8.8.8.0/24", "142.250.0.0/16"]
  },
  "validation_summary": {
    "overall_score": 85.5,
    "validation_results": [
      {"type": "source", "status": "passed", "score": 88},
      {"type": "validation", "status": "passed", "score": 83}
    ]
  }
}
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Settings
```bash
# Copy configuration template
cp config.env.example .env

# Edit .env with your settings:
# - Database credentials
# - OpenAI API key
# - LangChain API key
```

### 3. Initialize Database
```bash
# Create PostgreSQL database
createdb company_data

# Initialize tables
python main.py --init-db
```

### 4. Run Collection
```bash
# Process Alphabet Inc. (default)
python main.py

# Process specific company
python main.py --company "Microsoft Corporation"

# Process multiple companies
python main.py --companies "Alphabet Inc." "Microsoft Corporation"
```

## 📈 Pipeline Flow

```
Wikipedia Data → Collection → Preparation → Validation → Database
     ↓              ↓            ↓            ↓           ↓
  Raw JSON → Structured Data → Enhanced Data → Validated Data → Stored Data
```

### Detailed Flow
1. **Collection**: Extract company data from Wikipedia
2. **Preparation Stage 1**: Generate search terms and hierarchy
3. **Preparation Stage 2**: Associate domains with logical parents
4. **Preparation Stage 3**: Check for additional digital assets
5. **Preparation Stage 4**: Enumerate all name representations
6. **Validation Stage 1**: Verify search terms against digital assets
7. **Validation Stage 2**: Complete hierarchy validation
8. **Storage**: Save to PostgreSQL with full audit trail

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_pipeline.py::TestWikipediaCollector::test_collect_company_data_success
```

## 📊 Quality Metrics

### Validation Scoring
- **Source Validation**: 0-100 (search terms → digital assets)
- **Final Validation**: 0-100 (hierarchy completeness)
- **Overall Score**: Average of all validation scores
- **Pass Threshold**: 70+ overall score

### Data Quality Indicators
- ✅ Search term coverage
- ✅ Domain verification
- ✅ ASN/Netblock validation
- ✅ Cross-reference consistency
- ✅ Hierarchy completeness

## 🔧 Configuration Options

### Key Settings
```env
# Target Company
TARGET_COMPANY=Alphabet Inc.
COMPANY_SEARCH_TERMS=Alphabet,Google,Alphabet Holdings,Google LLC

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/company_data

# AI Services
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key

# Processing
MAX_RETRIES=3
REQUEST_DELAY=1.0
BATCH_SIZE=10
```

## 🎉 Success Criteria

### Functional Requirements
- ✅ Collect company data from Wikipedia
- ✅ Process through 4-stage preparation pipeline
- ✅ Validate through 2-stage validation process
- ✅ Store in PostgreSQL database
- ✅ Provide JSON output format
- ✅ Support agentic AI orchestration

### Quality Requirements
- ✅ Data accuracy > 80%
- ✅ Processing pipeline completion
- ✅ Validation score > 70%
- ✅ Database integrity
- ✅ Error handling and logging

## 🚀 Future Enhancements

### Potential Improvements
- **Additional Data Sources**: SEC filings, company websites, news articles
- **Enhanced AI**: More sophisticated reasoning and decision making
- **Real-time Updates**: Continuous data monitoring and updates
- **Advanced Analytics**: Trend analysis, competitive intelligence
- **API Interface**: REST API for external integrations
- **Web Dashboard**: User interface for data visualization

## 📝 Conclusion

This prototype successfully demonstrates a comprehensive agentic AI system for company data collection, preparation, and validation. The system is specifically designed for Alphabet Holdings but can be easily adapted for other companies. The modular architecture, comprehensive testing, and detailed documentation make it a solid foundation for production deployment.

**Key Achievements:**
- ✅ Complete end-to-end pipeline
- ✅ Agentic AI orchestration
- ✅ Comprehensive data validation
- ✅ PostgreSQL integration
- ✅ JSON data format
- ✅ Extensive documentation
- ✅ Test coverage
- ✅ Production-ready architecture
