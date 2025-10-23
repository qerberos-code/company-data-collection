from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class Company(Base):
    """Main company entity."""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255), nullable=True)
    colloquial_name = Column(String(255), nullable=True)
    parent_company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_company = relationship("Company", remote_side=[id], backref="subsidiaries")
    domains = relationship("Domain", back_populates="company")
    acquisitions = relationship("Acquisition", back_populates="acquirer")
    brands = relationship("Brand", back_populates="company")
    data_sources = relationship("DataSource", back_populates="company")


class Domain(Base):
    """Domain names associated with companies."""
    __tablename__ = "domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    domain_name = Column(String(255), nullable=False, index=True)
    domain_type = Column(String(50), nullable=True)  # primary, subsidiary, acquisition, etc.
    asn = Column(String(50), nullable=True)
    netblock = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="domains")


class Acquisition(Base):
    """Company acquisitions and mergers."""
    __tablename__ = "acquisitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    acquirer_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    acquired_company_name = Column(String(255), nullable=False)
    acquisition_date = Column(DateTime, nullable=True)
    acquisition_value = Column(String(100), nullable=True)
    acquisition_type = Column(String(50), nullable=True)  # merger, acquisition, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    acquirer = relationship("Company", back_populates="acquisitions")


class Brand(Base):
    """Brands and products associated with companies."""
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    brand_name = Column(String(255), nullable=False, index=True)
    brand_type = Column(String(50), nullable=True)  # product, service, platform, etc.
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="brands")


class DataSource(Base):
    """Sources of collected data."""
    __tablename__ = "data_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # wikipedia, official_site, etc.
    source_url = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 1-100
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="data_sources")


class ProcessingStage(Base):
    """Track data processing stages."""
    __tablename__ = "processing_stages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    stage_name = Column(String(100), nullable=False)  # collection, preparation, validation
    stage_status = Column(String(50), nullable=False)  # pending, in_progress, completed, failed
    stage_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company")


class ValidationResult(Base):
    """Data validation results."""
    __tablename__ = "validation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    validation_type = Column(String(100), nullable=False)  # source, recon, etc.
    validation_status = Column(String(50), nullable=False)  # passed, failed, warning
    validation_details = Column(JSON, nullable=True)
    validation_score = Column(Integer, nullable=True)  # 1-100
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
