import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from app.core.event_processing_service import EventProcessingService, DataAnalyticsService

@pytest.fixture
def mock_database_repo():
    repo = Mock()
    repo.save_user_analytics_event = AsyncMock(return_value=uuid4())
    repo.save_chemical_research_event = AsyncMock(return_value=uuid4())
    repo.create_event_processing_status = AsyncMock(return_value=uuid4())
    repo.update_event_processing_status = AsyncMock()
    repo.get_user_analytics_events = AsyncMock(return_value=[])
    repo.get_chemical_research_events = AsyncMock(return_value=[])
    return repo

@pytest.fixture
def mock_llm_service():
    service = Mock()
    service.extract_chemical_properties = AsyncMock(return_value={
        "color": "blue",
        "ph": 7.0,
        "confidence_score": 0.95
    })
    return service

@pytest.fixture
def event_processing_service(mock_database_repo, mock_llm_service):
    return EventProcessingService(mock_database_repo, mock_llm_service)

@pytest.fixture
def analytics_service(mock_database_repo):
    return DataAnalyticsService(mock_database_repo)

@pytest.fixture
def sample_user_analytics_event():
    return {
        "user_id": "test_user_123",
        "event_type": "page_view",
        "timestamp": "2024-01-01T12:00:00Z",
        "metadata": {"page": "/dashboard"}
    }

@pytest.fixture
def sample_chemical_research_event():
    return {
        "molecule_id": "mol_123",
        "researcher": "Dr. Test",
        "data": {"formula": "H2O", "weight": 18.015},
        "timestamp": "2024-01-01T12:00:00Z"
    }

class TestEventProcessingService:
    
    @pytest.mark.asyncio
    async def test_process_user_analytics_event_success(
        self, 
        event_processing_service, 
        mock_database_repo, 
        sample_user_analytics_event
    ):
        # Act
        result = await event_processing_service.process_user_analytics_event(sample_user_analytics_event)
        
        # Assert
        assert result is not None
        mock_database_repo.save_user_analytics_event.assert_called_once_with(sample_user_analytics_event)
        mock_database_repo.create_event_processing_status.assert_called_once()
        mock_database_repo.update_event_processing_status.assert_called_with(
            result, 'completed'
        )
    
    @pytest.mark.asyncio
    async def test_process_user_analytics_event_missing_field(
        self, 
        event_processing_service
    ):
        # Arrange
        invalid_event = {"user_id": "test_user"}  # Missing required fields
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required field"):
            await event_processing_service.process_user_analytics_event(invalid_event)
    
    @pytest.mark.asyncio
    async def test_process_chemical_research_event_success(
        self, 
        event_processing_service, 
        mock_database_repo,
        mock_llm_service,
        sample_chemical_research_event
    ):
        # Act
        result = await event_processing_service.process_chemical_research_event(sample_chemical_research_event)
        
        # Assert
        assert result is not None
        mock_llm_service.extract_chemical_properties.assert_called_once_with(
            sample_chemical_research_event["data"]
        )
        mock_database_repo.save_chemical_research_event.assert_called_once()
        
        # Check that LLM properties were added
        saved_event = mock_database_repo.save_chemical_research_event.call_args[0][0]
        assert "llm_properties" in saved_event
    
    @pytest.mark.asyncio
    async def test_process_chemical_research_event_missing_field(
        self, 
        event_processing_service
    ):
        # Arrange
        invalid_event = {"molecule_id": "mol_123"}  # Missing required fields
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required field"):
            await event_processing_service.process_chemical_research_event(invalid_event)

class TestDataAnalyticsService:
    
    @pytest.mark.asyncio
    async def test_get_user_analytics_summary(
        self, 
        analytics_service, 
        mock_database_repo
    ):
        # Arrange
        mock_events = [
            {"event_type": "page_view", "user_id": "test_user"},
            {"event_type": "click", "user_id": "test_user"},
            {"event_type": "page_view", "user_id": "test_user"},
        ]
        mock_database_repo.get_user_analytics_events.return_value = mock_events
        
        # Act
        result = await analytics_service.get_user_analytics_summary("test_user")
        
        # Assert
        assert result["user_id"] == "test_user"
        assert result["total_events"] == 3
        assert result["event_types"]["page_view"] == 2
        assert result["event_types"]["click"] == 1
        assert len(result["recent_events"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_researcher_summary(
        self, 
        analytics_service, 
        mock_database_repo
    ):
        # Arrange
        mock_events = [
            {"molecule_id": "mol_1", "researcher": "Dr. Test"},
            {"molecule_id": "mol_2", "researcher": "Dr. Test"},
            {"molecule_id": "mol_1", "researcher": "Dr. Test"},
        ]
        mock_database_repo.get_chemical_research_events.return_value = mock_events
        
        # Act
        result = await analytics_service.get_researcher_summary("Dr. Test")
        
        # Assert
        assert result["researcher"] == "Dr. Test"
        assert result["total_experiments"] == 3
        assert result["unique_molecules"] == 2
        assert "mol_1" in result["molecules_list"]
        assert "mol_2" in result["molecules_list"]
