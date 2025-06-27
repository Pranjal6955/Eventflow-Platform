from celery import Celery
import asyncio
import logging
from typing import Dict, Any

from app.config.settings import settings
from app.infrastructure.postgresql_repository import PostgreSQLRepository
from app.infrastructure.llm_service import MockLLMService
from app.core.event_processing_service import EventProcessingService

logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery(
    'event_subscriber',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.api_worker.handlers']
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_default_retry_delay=settings.RETRY_DELAY,
    task_max_retries=settings.MAX_RETRIES,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Initialize services (will be used by tasks)
database_repo = PostgreSQLRepository()
llm_service = MockLLMService()
event_processing_service = EventProcessingService(database_repo, llm_service)

@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_user_analytics_event_task(self, event_data: Dict[str, Any]):
    """Celery task for processing user analytics events"""
    try:
        logger.info(f"Processing user analytics event task: {event_data.get('user_id')}")
        
        # Run the async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                event_processing_service.process_user_analytics_event(event_data)
            )
            logger.info(f"Successfully processed user analytics event: {result}")
            return str(result)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in user analytics task: {str(e)}")
        raise self.retry(exc=e)

@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_chemical_research_event_task(self, event_data: Dict[str, Any]):
    """Celery task for processing chemical research events"""
    try:
        logger.info(f"Processing chemical research event task: {event_data.get('molecule_id')}")
        
        # Run the async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                event_processing_service.process_chemical_research_event(event_data)
            )
            logger.info(f"Successfully processed chemical research event: {result}")
            return str(result)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in chemical research task: {str(e)}")
        raise self.retry(exc=e)

# Event type to task mapping
EVENT_HANDLERS = {
    'user_analytics': process_user_analytics_event_task,
    'chemical_research': process_chemical_research_event_task,
}

def dispatch_event(event_data: Dict[str, Any]):
    """Dispatch event to appropriate Celery task"""
    event_type = event_data.get('type')
    
    if event_type not in EVENT_HANDLERS:
        logger.error(f"Unknown event type: {event_type}")
        raise ValueError(f"Unknown event type: {event_type}")
    
    handler = EVENT_HANDLERS[event_type]
    logger.info(f"Dispatching {event_type} event to Celery task")
    
    # Submit task to Celery
    task_result = handler.delay(event_data)
    logger.info(f"Task submitted with ID: {task_result.id}")
    
    return task_result.id
