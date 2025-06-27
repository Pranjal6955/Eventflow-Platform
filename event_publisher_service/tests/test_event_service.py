import pytest
from unittest.mock import Mock, patch
from app.core.event_service import EventService, get_event_service

class TestEventService:
    
    def test_publish_event_success(self, mock_event_service):
        # Arrange
        event_data = {"type": "test", "data": "sample"}
        
        # Act
        mock_event_service.publish_event(event_data)
        
        # Assert
        mock_event_service.event_queue.enqueue.assert_called_once_with(event_data)

    def test_publish_event_queue_failure(self, mock_event_queue):
        # Arrange
        mock_event_queue.enqueue.side_effect = Exception("Queue error")
        service = EventService(mock_event_queue)
        event_data = {"type": "test", "data": "sample"}
        
        # Act & Assert
        with pytest.raises(Exception, match="Queue error"):
            service.publish_event(event_data)

    @patch('app.core.event_service.KafkaEventQueue')
    @patch('app.core.event_service.settings')
    def test_get_event_service(self, mock_settings, mock_kafka_queue):
        # Arrange
        mock_settings.KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
        mock_settings.KAFKA_TOPIC = "test_topic"
        mock_queue_instance = Mock()
        mock_kafka_queue.return_value = mock_queue_instance
        
        # Act
        service = get_event_service()
        
        # Assert
        assert isinstance(service, EventService)
        mock_kafka_queue.assert_called_once_with(
            bootstrap_servers="localhost:9092",
            topic="test_topic"
        )
