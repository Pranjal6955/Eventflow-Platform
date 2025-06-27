from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMService(ABC):
    """Abstract base class for LLM service integration"""
    
    @abstractmethod
    async def extract_chemical_properties(self, chemical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chemical properties using LLM"""
        pass

class MockLLMService(LLMService):
    """Mock LLM service for demonstration purposes"""
    
    async def extract_chemical_properties(self, chemical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation that returns dummy chemical properties"""
        formula = chemical_data.get("formula", "Unknown")
        
        # Mock properties based on common chemicals
        mock_properties = {
            "H2O": {
                "color": "colorless",
                "ph": 7.0,
                "boiling_point": "100°C",
                "melting_point": "0°C",
                "density": "1.0 g/cm³",
                "solubility": "miscible with water",
                "toxicity": "non-toxic"
            },
            "NaCl": {
                "color": "white",
                "ph": 7.0,
                "boiling_point": "1465°C",
                "melting_point": "801°C",
                "density": "2.17 g/cm³",
                "solubility": "36 g/100mL water",
                "toxicity": "low toxicity"
            },
            "CO2": {
                "color": "colorless",
                "ph": 5.6,
                "boiling_point": "-78.5°C",
                "melting_point": "-78.5°C",
                "density": "1.98 g/L",
                "solubility": "1.7 g/L water",
                "toxicity": "asphyxiant in high concentrations"
            }
        }
        
        # Return mock properties or default values
        properties = mock_properties.get(formula, {
            "color": "unknown",
            "ph": None,
            "boiling_point": "unknown",
            "melting_point": "unknown",
            "density": "unknown",
            "solubility": "unknown",
            "toxicity": "unknown"
        })
        
        # Add analysis metadata
        properties.update({
            "analysis_timestamp": "2024-01-01T12:00:00Z",
            "confidence_score": 0.95,
            "model_version": "mock-llm-v1.0",
            "extracted_from": chemical_data
        })
        
        return properties

class HTTPLLMService(LLMService):
    """HTTP-based LLM service implementation"""
    
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key
    
    async def extract_chemical_properties(self, chemical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chemical properties using external LLM API"""
        import httpx
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            payload = {
                "prompt": f"Extract chemical properties for: {chemical_data}",
                "chemical_data": chemical_data
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/extract-properties",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling LLM service: {str(e)}")
            # Fallback to mock service
            mock_service = MockLLMService()
            return await mock_service.extract_chemical_properties(chemical_data)
        except Exception as e:
            logger.error(f"Error calling LLM service: {str(e)}")
            # Fallback to mock service
            mock_service = MockLLMService()
            return await mock_service.extract_chemical_properties(chemical_data)
