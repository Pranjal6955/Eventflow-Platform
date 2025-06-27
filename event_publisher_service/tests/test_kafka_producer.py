import pytest
from unittest.mock import Mock, patch, MagicMock
from app.infrastructure.kafka_producer import KafkaEventQueue

class TestKafkaEventQueue:
    
    @patch('app.infrastructure.kafka_producer.Producer')
    def test_kafka_event_queue_initialization(self, mock_producer_class):
        # Arrange
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer
        
        # Act
        queue = KafkaEventQueue("localhost:9092", "test_topic")
        
        # Assert
        assert queue.topic == "test_topic"
        mock_producer_class.assert_called_once()

    @patch('app.infrastructure.kafka_producer.Producer')
    def test_enqueue_event_success(self, mock_producer_class):
        # Arrange
        mock_producer = Mock()
        mock_producer_class.return_value = mock_producer
        queue = KafkaEventQueue("localhost:9092", "test_topic")
        event_data = {"type": "test", "data": "sample"}
        
        # Act
        queue.enqueue(event_data)
        
        # Assert
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.infrastructure.kafka_producer.Producer')
    def test_enqueue_event_kafka_error(self, mock_producer_class):
        # Arrange
        mock_producer = Mock()
        mock_producer.produce.side_effect = Exception("Kafka connection error")
        mock_producer_class.return_value = mock_producer
        queue = KafkaEventQueue("localhost:9092", "test_topic")
        event_data = {"type": "test", "data": "sample"}
        
        # Act & Assert
        with pytest.raises(Exception, match="Kafka connection error"):
            queue.enqueue(event_data)
