import pytest
from app.api.transformers import transform_user_analytics_event, transform_chemical_research_event
from app.api.models import UserAnalyticsEvent, ChemicalResearchEvent

class TestTransformers:
    
    def test_transform_user_analytics_event_with_metadata(self):
        # Arrange
        event = UserAnalyticsEvent(
            user_id="user_123",
            event_type="page_view",
            timestamp="2024-01-01T12:00:00Z",
            metadata={"page": "/dashboard", "source": "web"}
        )
        
        # Act
        result = transform_user_analytics_event(event)
        
        # Assert
        expected = {
            "type": "user_analytics",
            "user_id": "user_123",
            "event_type": "page_view",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"page": "/dashboard", "source": "web"}
        }
        assert result == expected

    def test_transform_user_analytics_event_without_metadata(self):
        # Arrange
        event = UserAnalyticsEvent(
            user_id="user_123",
            event_type="click",
            timestamp="2024-01-01T12:00:00Z"
        )
        
        # Act
        result = transform_user_analytics_event(event)
        
        # Assert
        expected = {
            "type": "user_analytics",
            "user_id": "user_123",
            "event_type": "click",
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {}
        }
        assert result == expected

    def test_transform_chemical_research_event(self):
        # Arrange
        event = ChemicalResearchEvent(
            molecule_id="mol_123",
            researcher="Dr. Smith",
            data={"formula": "H2O", "weight": 18.015, "state": "liquid"},
            timestamp="2024-01-01T12:00:00Z"
        )
        
        # Act
        result = transform_chemical_research_event(event)
        
        # Assert
        expected = {
            "type": "chemical_research",
            "molecule_id": "mol_123",
            "researcher": "Dr. Smith",
            "data": {"formula": "H2O", "weight": 18.015, "state": "liquid"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
        assert result == expected
