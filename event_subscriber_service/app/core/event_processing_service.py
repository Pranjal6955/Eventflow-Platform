from typing import Dict, Any
import logging
from uuid import UUID
from app.infrastructure.database_repository import DatabaseRepository
from app.infrastructure.llm_service import LLMService

logger = logging.getLogger(__name__)

class EventProcessingService:
    """Core service for processing different types of events"""
    
    def __init__(self, database_repo: DatabaseRepository, llm_service: LLMService):
        self.database_repo = database_repo
        self.llm_service = llm_service
    
    async def process_user_analytics_event(self, event_data: Dict[str, Any]) -> UUID:
        """Process user analytics event"""
        try:
            logger.info(f"Processing user analytics event for user: {event_data.get('user_id')}")
            
            # Validate required fields
            required_fields = ['user_id', 'event_type', 'timestamp']
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Save to database
            event_id = await self.database_repo.save_user_analytics_event(event_data)
            
            # Create processing status
            await self.database_repo.create_event_processing_status(event_id, 'user_analytics')
            
            # Update status to completed
            await self.database_repo.update_event_processing_status(event_id, 'completed')
            
            logger.info(f"Successfully processed user analytics event: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error processing user analytics event: {str(e)}")
            raise
    
    async def process_chemical_research_event(self, event_data: Dict[str, Any]) -> UUID:
        """Process chemical research event with LLM enhancement"""
        try:
            logger.info(f"Processing chemical research event for molecule: {event_data.get('molecule_id')}")
            
            # Validate required fields
            required_fields = ['molecule_id', 'researcher', 'data', 'timestamp']
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Extract chemical properties using LLM
            logger.info("Extracting chemical properties using LLM")
            llm_properties = await self.llm_service.extract_chemical_properties(event_data['data'])
            
            # Add LLM properties to event data
            event_data['llm_properties'] = llm_properties
            
            # Save to database
            event_id = await self.database_repo.save_chemical_research_event(event_data)
            
            # Create processing status
            await self.database_repo.create_event_processing_status(event_id, 'chemical_research')
            
            # Update status to completed
            await self.database_repo.update_event_processing_status(event_id, 'completed')
            
            logger.info(f"Successfully processed chemical research event: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error processing chemical research event: {str(e)}")
            raise

class DataAnalyticsService:
    """Service for analytics and data processing functions"""
    
    def __init__(self, database_repo: DatabaseRepository):
        self.database_repo = database_repo
    
    async def get_user_analytics_summary(self, user_id: str) -> Dict[str, Any]:
        """Get analytics summary for a user"""
        try:
            events = await self.database_repo.get_user_analytics_events(user_id, limit=100)
            
            # Calculate analytics
            total_events = len(events)
            event_types = {}
            
            for event in events:
                event_type = event['event_type']
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            return {
                "user_id": user_id,
                "total_events": total_events,
                "event_types": event_types,
                "recent_events": events[:10]
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics summary: {str(e)}")
            raise
    
    async def get_researcher_summary(self, researcher: str) -> Dict[str, Any]:
        """Get research summary for a researcher"""
        try:
            events = await self.database_repo.get_chemical_research_events(researcher, limit=100)
            
            # Calculate analytics
            total_experiments = len(events)
            molecules_studied = set(event['molecule_id'] for event in events)
            
            return {
                "researcher": researcher,
                "total_experiments": total_experiments,
                "unique_molecules": len(molecules_studied),
                "molecules_list": list(molecules_studied),
                "recent_experiments": events[:10]
            }
            
        except Exception as e:
            logger.error(f"Error getting researcher summary: {str(e)}")
            raise
