import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_analytics_service():
    service = Mock()
    service.get_user_analytics_summary = AsyncMock()
    service.get_researcher_summary = AsyncMock()
    return service

@pytest.fixture
def mock_database_repo():
    repo = Mock()
    repo.get_user_analytics_events = AsyncMock()
    repo.get_chemical_research_events = AsyncMock()
    return repo

class TestAPIEndpoints:
    
    def test_health_check(self, client):
        # Act
        response = client.get("/healthz")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "event_subscriber"}
    
    @patch('app.main.analytics_service')
    def test_get_user_analytics_success(self, mock_service, client):
        # Arrange
        mock_service.get_user_analytics_summary.return_value = {
            "user_id": "test_user",
            "total_events": 10,
            "event_types": {"click": 5, "view": 5}
        }
        
        # Act
        response = client.get("/api/v1/analytics/user/test_user")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["total_events"] == 10
    
    @patch('app.main.analytics_service')
    def test_get_user_analytics_error(self, mock_service, client):
        # Arrange
        mock_service.get_user_analytics_summary.side_effect = Exception("Database error")
        
        # Act
        response = client.get("/api/v1/analytics/user/test_user")
        
        # Assert
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
    
    @patch('app.main.analytics_service')
    def test_get_researcher_analytics_success(self, mock_service, client):
        # Arrange
        mock_service.get_researcher_summary.return_value = {
            "researcher": "Dr. Test",
            "total_experiments": 5,
            "unique_molecules": 3
        }
        
        # Act
        response = client.get("/api/v1/analytics/researcher/Dr.%20Test")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["researcher"] == "Dr. Test"
        assert data["total_experiments"] == 5
    
    @patch('app.main.database_repo')
    def test_get_user_events_success(self, mock_repo, client):
        # Arrange
        mock_repo.get_user_analytics_events.return_value = [
            {"id": "1", "event_type": "click", "timestamp": "2024-01-01T12:00:00Z"},
            {"id": "2", "event_type": "view", "timestamp": "2024-01-01T12:01:00Z"}
        ]
        
        # Act
        response = client.get("/api/v1/events/user/test_user?limit=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert len(data["events"]) == 2
    
    @patch('app.main.database_repo')
    def test_get_researcher_events_success(self, mock_repo, client):
        # Arrange
        mock_repo.get_chemical_research_events.return_value = [
            {"id": "1", "molecule_id": "mol_1", "researcher": "Dr. Test"},
            {"id": "2", "molecule_id": "mol_2", "researcher": "Dr. Test"}
        ]
        
        # Act
        response = client.get("/api/v1/events/researcher/Dr.%20Test?limit=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["researcher"] == "Dr. Test"
        assert len(data["events"]) == 2
