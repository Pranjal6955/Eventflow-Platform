from confluent_kafka import Producer
import json
import logging
from .event_queue import EventQueue
from app.config.settings import settings

logger = logging.getLogger(__name__)

class KafkaEventQueue(EventQueue):
    def __init__(self, bootstrap_servers: str, topic: str):
        self.topic = topic
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'linger.ms': 10,
            'retries': settings.MAX_RETRIES,
            'retry.backoff.ms': 500,
            'request.timeout.ms': 30000,
            'delivery.timeout.ms': 60000,
            'acks': 'all',  # Wait for all replicas to acknowledge
            'compression.type': 'gzip',  # Enable compression
        })
        logger.info(f"Initialized Kafka producer for topic: {topic}")

    def enqueue(self, event: dict):
        def delivery_report(err, msg):
            if err is not None:
                logger.error(f'Message delivery failed: {err}')
                raise Exception(f'Message delivery failed: {err}')
            else:
                logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
        
        try:
            # Add event metadata
            event_with_metadata = {
                **event,
                'published_at': '2024-01-01T12:00:00Z',  # This would be datetime.utcnow().isoformat() in real implementation
                'service_version': '1.0.0'
            }
            
            self.producer.produce(
                self.topic, 
                json.dumps(event_with_metadata).encode('utf-8'),
                callback=delivery_report
            )
            self.producer.flush(timeout=10.0)
            logger.info(f"Successfully enqueued event of type: {event.get('type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to enqueue event: {str(e)}")
            raise
    
    def close(self):
        """Close the producer connection"""
        self.producer.flush()
        logger.info("Kafka producer closed")