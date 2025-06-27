import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.core.event_service import EventService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_event_queue():
    return Mock()

@pytest.fixture
def mock_event_service(mock_event_queue):
    return EventService(mock_event_queue)

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
