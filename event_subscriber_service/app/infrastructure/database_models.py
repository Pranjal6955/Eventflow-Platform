from sqlalchemy import Column, String, DateTime, Text, JSON, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class UserAnalyticsEvent(Base):
    __tablename__ = 'user_analytics_events'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    page_url = Column(String)
    user_agent = Column(String)
    session_id = Column(String)
    timestamp = Column(DateTime, nullable=False)
    event_metadata = Column(JSON)  # Changed from 'metadata' to 'event_metadata'
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ChemicalResearchEvent(Base):
    __tablename__ = 'chemical_research_events'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    molecule_id = Column(String, nullable=False, index=True)
    researcher = Column(String, nullable=False, index=True)
    experiment_type = Column(String, nullable=False)
    properties = Column(JSON)
    results = Column(JSON)
    timestamp = Column(DateTime, nullable=False)
    event_metadata = Column(JSON)  # Changed from 'metadata' to 'event_metadata'
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class EventProcessingStatus(Base):
    __tablename__ = 'event_processing_status'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    status = Column(String, nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
