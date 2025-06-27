from app.infrastructure.event_queue import EventQueue
from app.config.settings import settings

class EventService:
    def __init__(self, event_queue: EventQueue):
        self.event_queue = event_queue

    def publish_event(self, event: dict):
        # Add business rule validation here if needed
        self.event_queue.enqueue(event)

def get_event_service():
    from app.infrastructure.kafka_producer import KafkaEventQueue
    return EventService(KafkaEventQueue(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        topic=settings.KAFKA_TOPIC
    )) 