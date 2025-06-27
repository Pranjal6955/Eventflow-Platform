import asyncio
import logging
from typing import Dict, Any
from app.infrastructure.kafka_consumer import KafkaEventConsumer
from app.api_worker.handlers import dispatch_event
from app.config.settings import settings

logger = logging.getLogger(__name__)

class EventWorker:
    """Main worker class that coordinates Kafka consumption and Celery task dispatch"""
    
    def __init__(self):
        self.kafka_consumer = KafkaEventConsumer(self.handle_event)
    
    async def handle_event(self, event_data: Dict[str, Any]):
        """Handle incoming events from Kafka"""
        try:
            logger.info(f"Handling event: {event_data.get('type', 'unknown')}")
            
            # Dispatch to Celery task
            task_id = dispatch_event(event_data)
            logger.info(f"Event dispatched to task: {task_id}")
            
        except Exception as e:
            logger.error(f"Error handling event: {str(e)}")
            # Could implement dead letter queue here
    
    def start(self):
        """Start the worker"""
        logger.info("Starting Event Subscriber Worker")
        
        try:
            # Start Kafka consumer in the main thread
            self.kafka_consumer.start_consuming()
        except KeyboardInterrupt:
            logger.info("Worker interrupted by user")
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the worker"""
        logger.info("Stopping Event Subscriber Worker")
        self.kafka_consumer.stop_consuming()

def main():
    """Main entry point for the worker"""
    worker = EventWorker()
    worker.start()

if __name__ == "__main__":
    main()
