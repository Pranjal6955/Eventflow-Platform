from sqlalchemy import create_engine, select, update, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
from datetime import datetime

from .database_repository import DatabaseRepository
from .database_models import UserAnalyticsEvent, ChemicalResearchEvent, EventProcessingStatus
from app.config.settings import settings

logger = logging.getLogger(__name__)

class PostgreSQLRepository(DatabaseRepository):
    """PostgreSQL implementation of the database repository"""
    
    def __init__(self):
        # Convert sync DSN to async DSN
        async_dsn = settings.POSTGRES_DSN.replace("postgresql://", "postgresql+asyncpg://")
        self.async_engine = create_async_engine(async_dsn, echo=False)
        self.async_session_factory = async_sessionmaker(
            self.async_engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        self.engine = create_engine(settings.POSTGRES_DSN)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    async def save_user_analytics_event(self, event_data: Dict[str, Any]) -> UUID:
        """Save user analytics event to database"""
        async with self.async_session_factory() as session:
            try:
                event = UserAnalyticsEvent(
                    user_id=event_data["user_id"],
                    event_type=event_data["event_type"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"].replace('Z', '+00:00')),
                    metadata=event_data.get("metadata", {})
                )
                session.add(event)
                await session.commit()
                await session.refresh(event)
                logger.info(f"Saved user analytics event: {event.id}")
                return event.id
            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving user analytics event: {str(e)}")
                raise
    
    async def save_chemical_research_event(self, event_data: Dict[str, Any]) -> UUID:
        """Save chemical research event to database"""
        async with self.async_session_factory() as session:
            try:
                event = ChemicalResearchEvent(
                    molecule_id=event_data["molecule_id"],
                    researcher=event_data["researcher"],
                    data=event_data["data"],
                    timestamp=datetime.fromisoformat(event_data["timestamp"].replace('Z', '+00:00')),
                    llm_properties=event_data.get("llm_properties")
                )
                session.add(event)
                await session.commit()
                await session.refresh(event)
                logger.info(f"Saved chemical research event: {event.id}")
                return event.id
            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving chemical research event: {str(e)}")
                raise
    
    async def get_user_analytics_events(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user analytics events for a specific user"""
        async with self.async_session_factory() as session:
            try:
                query = (
                    select(UserAnalyticsEvent)
                    .where(UserAnalyticsEvent.user_id == user_id)
                    .order_by(UserAnalyticsEvent.timestamp.desc())
                    .limit(limit)
                )
                result = await session.execute(query)
                events = result.scalars().all()
                
                return [
                    {
                        "id": str(event.id),
                        "user_id": event.user_id,
                        "event_type": event.event_type,
                        "timestamp": event.timestamp.isoformat(),
                        "metadata": event.metadata,
                        "processed_at": event.processed_at.isoformat() if event.processed_at else None
                    }
                    for event in events
                ]
            except Exception as e:
                logger.error(f"Error getting user analytics events: {str(e)}")
                raise
    
    async def get_chemical_research_events(self, researcher: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chemical research events for a specific researcher"""
        async with self.async_session_factory() as session:
            try:
                query = (
                    select(ChemicalResearchEvent)
                    .where(ChemicalResearchEvent.researcher == researcher)
                    .order_by(ChemicalResearchEvent.timestamp.desc())
                    .limit(limit)
                )
                result = await session.execute(query)
                events = result.scalars().all()
                
                return [
                    {
                        "id": str(event.id),
                        "molecule_id": event.molecule_id,
                        "researcher": event.researcher,
                        "data": event.data,
                        "timestamp": event.timestamp.isoformat(),
                        "llm_properties": event.llm_properties,
                        "processed_at": event.processed_at.isoformat() if event.processed_at else None
                    }
                    for event in events
                ]
            except Exception as e:
                logger.error(f"Error getting chemical research events: {str(e)}")
                raise
    
    async def create_event_processing_status(self, event_id: UUID, event_type: str) -> UUID:
        """Create event processing status record"""
        async with self.async_session_factory() as session:
            try:
                status_record = EventProcessingStatus(
                    event_id=event_id,
                    event_type=event_type,
                    status='pending'
                )
                session.add(status_record)
                await session.commit()
                await session.refresh(status_record)
                return status_record.id
            except Exception as e:
                await session.rollback()
                logger.error(f"Error creating event processing status: {str(e)}")
                raise
    
    async def update_event_processing_status(
        self, 
        event_id: UUID, 
        status: str, 
        error_message: Optional[str] = None
    ):
        """Update event processing status"""
        async with self.async_session_factory() as session:
            try:
                query = (
                    update(EventProcessingStatus)
                    .where(EventProcessingStatus.event_id == event_id)
                    .values(
                        status=status,
                        error_message=error_message,
                        updated_at=datetime.utcnow()
                    )
                )
                await session.execute(query)
                await session.commit()
                logger.info(f"Updated event processing status for {event_id}: {status}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating event processing status: {str(e)}")
                raise
    
    async def store_user_analytics_event(self, event_data: Dict[str, Any]) -> str:
        """Store user analytics event"""
        session = self.SessionLocal()
        try:
            event = UserAnalyticsEvent(
                user_id=event_data['user_id'],
                event_type=event_data['event_type'],
                page_url=event_data.get('page_url'),
                user_agent=event_data.get('user_agent'),
                session_id=event_data.get('session_id'),
                timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')),
                event_metadata=event_data.get('metadata', {})
            )
            session.add(event)
            session.commit()
            logger.info(f"Stored user analytics event: {event.id}")
            return event.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing user analytics event: {str(e)}")
            raise
        finally:
            session.close()
    
    async def store_chemical_research_event(self, event_data: Dict[str, Any]) -> str:
        """Store chemical research event"""
        session = self.SessionLocal()
        try:
            event = ChemicalResearchEvent(
                molecule_id=event_data['molecule_id'],
                researcher=event_data['researcher'],
                experiment_type=event_data['experiment_type'],
                properties=event_data.get('properties', {}),
                results=event_data.get('results', {}),
                timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')),
                event_metadata=event_data.get('metadata', {})
            )
            session.add(event)
            session.commit()
            logger.info(f"Stored chemical research event: {event.id}")
            return event.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing chemical research event: {str(e)}")
            raise
        finally:
            session.close()
    
    async def get_user_analytics_events(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user analytics events"""
        session = self.SessionLocal()
        try:
            events = session.query(UserAnalyticsEvent)\
                           .filter(UserAnalyticsEvent.user_id == user_id)\
                           .order_by(desc(UserAnalyticsEvent.timestamp))\
                           .limit(limit)\
                           .all()
            
            return [
                {
                    'id': event.id,
                    'event_type': event.event_type,
                    'page_url': event.page_url,
                    'timestamp': event.timestamp.isoformat(),
                    'metadata': event.event_metadata
                }
                for event in events
            ]
        except Exception as e:
            logger.error(f"Error retrieving user analytics events: {str(e)}")
            raise
        finally:
            session.close()
    
    async def get_chemical_research_events(self, researcher: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chemical research events"""
        session = self.SessionLocal()
        try:
            events = session.query(ChemicalResearchEvent)\
                           .filter(ChemicalResearchEvent.researcher == researcher)\
                           .order_by(desc(ChemicalResearchEvent.timestamp))\
                           .limit(limit)\
                           .all()
            
            return [
                {
                    'id': event.id,
                    'molecule_id': event.molecule_id,
                    'experiment_type': event.experiment_type,
                    'timestamp': event.timestamp.isoformat(),
                    'properties': event.properties,
                    'results': event.results
                }
                for event in events
            ]
        except Exception as e:
            logger.error(f"Error retrieving chemical research events: {str(e)}")
            raise
        finally:
            session.close()
