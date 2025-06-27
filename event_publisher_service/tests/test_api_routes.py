import pytest
from unittest.mock import patch, Mock
from fastapi import status

class TestUserAnalyticsRoutes:
    
    @patch('app.api.routes.get_event_service')
    def test_publish_user_analytics_event_success(self, mock_get_service, client, sample_user_analytics_event):
        # Arrange
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/v1/events/analytics", json=sample_user_analytics_event)
        
        # Assert
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"message": "Event published"}
        mock_service.publish_event.assert_called_once()

    @patch('app.api.routes.get_event_service')
    def test_publish_user_analytics_event_service_failure(self, mock_get_service, client, sample_user_analytics_event):
        # Arrange
        mock_service = Mock()
        mock_service.publish_event.side_effect = Exception("Kafka error")
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/v1/events/analytics", json=sample_user_analytics_event)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Kafka error" in response.json()["detail"]

    def test_publish_user_analytics_event_invalid_data(self, client):
        # Arrange
        invalid_event = {"user_id": "test"}  # Missing required fields
        
        # Act
        response = client.post("/api/v1/events/analytics", json=invalid_event)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestChemicalResearchRoutes:
    
    @patch('app.api.routes.get_event_service')
    def test_publish_chemical_research_event_success(self, mock_get_service, client, sample_chemical_research_event):
        # Arrange
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/v1/events/chemical", json=sample_chemical_research_event)
        
        # Assert
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"message": "Event published"}
        mock_service.publish_event.assert_called_once()

    @patch('app.api.routes.get_event_service')
    def test_publish_chemical_research_event_service_failure(self, mock_get_service, client, sample_chemical_research_event):
        # Arrange
        mock_service = Mock()
        mock_service.publish_event.side_effect = Exception("Kafka error")
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/v1/events/chemical", json=sample_chemical_research_event)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_publish_chemical_research_event_invalid_data(self, client):
        # Arrange
        invalid_event = {"molecule_id": "mol_123"}  # Missing required fields
        
        # Act
        response = client.post("/api/v1/events/chemical", json=invalid_event)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestHealthCheck:
    
    def test_health_check(self, client):
        # Act
        response = client.get("/healthz")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}
