import pytest
from unittest.mock import Mock, AsyncMock

# Test fixtures and configurations for the entire test suite

@pytest.fixture
def mock_database_repo():
    """Mock database repository for testing"""
    repo = Mock()
    repo.save_user_analytics_event = AsyncMock()
    repo.save_chemical_research_event = AsyncMock()
    repo.get_user_analytics_events = AsyncMock()
    repo.get_chemical_research_events = AsyncMock()
    repo.create_event_processing_status = AsyncMock()
    repo.update_event_processing_status = AsyncMock()
    return repo

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    service = Mock()
    service.extract_chemical_properties = AsyncMock(return_value={
        "color": "blue",
        "ph": 7.0,
        "confidence_score": 0.95
    })
    return service

@pytest.fixture
def sample_user_analytics_event():
    """Sample user analytics event data"""
    return {
        "user_id": "test_user_123",
        "event_type": "page_view",
        "timestamp": "2024-01-01T12:00:00Z",
        "metadata": {"page": "/dashboard", "source": "web"}
    }

@pytest.fixture
def sample_chemical_research_event():
    """Sample chemical research event data"""
    return {
        "molecule_id": "mol_123",
        "researcher": "Dr. Test",
        "data": {"formula": "H2O", "weight": 18.015, "state": "liquid"},
        "timestamp": "2024-01-01T12:00:00Z"
    }
