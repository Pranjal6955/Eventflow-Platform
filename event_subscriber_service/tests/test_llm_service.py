import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.infrastructure.llm_service import MockLLMService, HTTPLLMService

class TestMockLLMService:
    
    @pytest.mark.asyncio
    async def test_extract_chemical_properties_h2o(self):
        # Arrange
        service = MockLLMService()
        chemical_data = {"formula": "H2O", "weight": 18.015}
        
        # Act
        result = await service.extract_chemical_properties(chemical_data)
        
        # Assert
        assert result["color"] == "colorless"
        assert result["ph"] == 7.0
        assert result["boiling_point"] == "100°C"
        assert result["confidence_score"] == 0.95
        assert "analysis_timestamp" in result
        assert "model_version" in result
    
    @pytest.mark.asyncio
    async def test_extract_chemical_properties_unknown(self):
        # Arrange
        service = MockLLMService()
        chemical_data = {"formula": "UNKNOWN", "weight": 99.99}
        
        # Act
        result = await service.extract_chemical_properties(chemical_data)
        
        # Assert
        assert result["color"] == "unknown"
        assert result["ph"] is None
        assert result["confidence_score"] == 0.95

class TestHTTPLLMService:
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_extract_chemical_properties_success(self, mock_client):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            "color": "red",
            "ph": 8.5,
            "confidence": 0.92
        }
        mock_response.raise_for_status = Mock()
        
        mock_client_instance = Mock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        
        service = HTTPLLMService("http://test-api", "test-key")
        chemical_data = {"formula": "Fe2O3"}
        
        # Act
        result = await service.extract_chemical_properties(chemical_data)
        
        # Assert
        assert result["color"] == "red"
        assert result["ph"] == 8.5
        assert result["confidence"] == 0.92
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_extract_chemical_properties_http_error_fallback(self, mock_client):
        # Arrange
        mock_client_instance = Mock()
        mock_client_instance.post = AsyncMock(side_effect=Exception("HTTP Error"))
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        
        service = HTTPLLMService("http://test-api", "test-key")
        chemical_data = {"formula": "H2O"}
        
        # Act
        result = await service.extract_chemical_properties(chemical_data)
        
        # Assert - Should fallback to mock service
        assert result["color"] == "colorless"  # H2O properties from mock
        assert result["ph"] == 7.0
        assert "model_version" in result
