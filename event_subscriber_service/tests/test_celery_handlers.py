import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.api_worker.handlers import (
    process_user_analytics_event_task,
    process_chemical_research_event_task,
    dispatch_event,
    EVENT_HANDLERS
)

class TestCeleryHandlers:
    
    @patch('app.api_worker.handlers.event_processing_service')
    def test_process_user_analytics_event_task_success(self, mock_service):
        # Arrange
        mock_service.process_user_analytics_event = AsyncMock(return_value="event-id-123")
        event_data = {
            "user_id": "test_user",
            "event_type": "click",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Create a mock task instance
        mock_task = Mock()
        
        # Act
        result = process_user_analytics_event_task(mock_task, event_data)
        
        # Assert
        assert result == "event-id-123"
    
    @patch('app.api_worker.handlers.event_processing_service')
    def test_process_chemical_research_event_task_success(self, mock_service):
        # Arrange
        mock_service.process_chemical_research_event = AsyncMock(return_value="event-id-456")
        event_data = {
            "molecule_id": "mol_123",
            "researcher": "Dr. Test",
            "data": {"formula": "H2O"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Create a mock task instance
        mock_task = Mock()
        
        # Act
        result = process_chemical_research_event_task(mock_task, event_data)
        
        # Assert
        assert result == "event-id-456"
    
    def test_dispatch_event_user_analytics(self):
        # Arrange
        event_data = {"type": "user_analytics", "user_id": "test"}
        
        with patch.object(EVENT_HANDLERS['user_analytics'], 'delay') as mock_delay:
            mock_delay.return_value.id = "task-123"
            
            # Act
            result = dispatch_event(event_data)
            
            # Assert
            assert result == "task-123"
            mock_delay.assert_called_once_with(event_data)
    
    def test_dispatch_event_chemical_research(self):
        # Arrange
        event_data = {"type": "chemical_research", "molecule_id": "mol_123"}
        
        with patch.object(EVENT_HANDLERS['chemical_research'], 'delay') as mock_delay:
            mock_delay.return_value.id = "task-456"
            
            # Act
            result = dispatch_event(event_data)
            
            # Assert
            assert result == "task-456"
            mock_delay.assert_called_once_with(event_data)
    
    def test_dispatch_event_unknown_type(self):
        # Arrange
        event_data = {"type": "unknown_type"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unknown event type"):
            dispatch_event(event_data)
    
    def test_event_handlers_mapping(self):
        # Assert
        assert "user_analytics" in EVENT_HANDLERS
        assert "chemical_research" in EVENT_HANDLERS
        assert len(EVENT_HANDLERS) == 2
