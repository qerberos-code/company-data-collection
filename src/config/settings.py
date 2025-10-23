from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Database Configuration
    database_url: str = Field(default="postgresql://username:password@localhost:5432/company_data")
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="company_data")
    db_user: str = Field(default="username")
    db_password: str = Field(default="password")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None)
    
    # Google AI Studio Configuration
    google_ai_api_key: Optional[str] = Field(default=None)
    google_ai_model: str = Field(default="gemini-1.5-flash")
    
    # LangChain Configuration
    langchain_api_key: Optional[str] = Field(default=None)
    langchain_tracing_v2: bool = Field(default=True)
    langchain_project: str = Field(default="company-data-collection")
    
    # Wikipedia API Configuration
    wikipedia_user_agent: str = Field(default="CompanyDataCollector/1.0")
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/app.log")
    
    # Data Collection Configuration
    max_retries: int = Field(default=3)
    request_delay: float = Field(default=1.0)
    batch_size: int = Field(default=10)
    
    # Company Configuration
    target_company: str = Field(default="Alphabet Inc.")
    company_search_terms: str = Field(default="Alphabet,Google,Alphabet Holdings,Google LLC")
    
    def get_search_terms(self) -> List[str]:
        """Parse search terms from comma-separated string."""
        return [term.strip() for term in self.company_search_terms.split(',') if term.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
