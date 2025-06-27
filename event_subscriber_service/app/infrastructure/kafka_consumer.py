from confluent_kafka import Consumer, KafkaError
import json
import logging
import asyncio
from typing import Dict, Any, Callable
from app.config.settings import settings

logger = logging.getLogger(__name__)

class KafkaEventConsumer:
    """Kafka consumer for processing events"""
    
    def __init__(self, event_handler: Callable[[Dict[str, Any]], None]):
        self.event_handler = event_handler
        self.consumer = Consumer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'session.timeout.ms': 30000,
            'heartbeat.interval.ms': 10000,
        })
        self.consumer.subscribe([settings.KAFKA_TOPIC])
        self.running = False
    
    def start_consuming(self):
        """Start consuming messages from Kafka"""
        self.running = True
        logger.info(f"Starting Kafka consumer for topic: {settings.KAFKA_TOPIC}")
        
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info(f"End of partition reached {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                try:
                    # Decode message
                    event_data = json.loads(msg.value().decode('utf-8'))
                    logger.info(f"Received event: {event_data.get('type', 'unknown')}")
                    
                    # Process event asynchronously
                    asyncio.create_task(self.event_handler(event_data))
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.consumer.close()
            logger.info("Kafka consumer closed")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.running = False
