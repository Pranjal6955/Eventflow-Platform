from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

class LLMService(ABC):
    """Abstract base class for LLM service integration"""
    
    @abstractmethod
    async def extract_chemical_properties(self, chemical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chemical properties using LLM"""
        pass

class MockLLMService:
    """Mock LLM service for testing purposes"""
    
    async def analyze_user_behavior(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock user behavior analysis"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'analysis': 'Mock user behavior analysis',
            'insights': [
                'User is actively browsing',
                'High engagement detected'
            ],
            'recommendations': [
                'Show related content',
                'Optimize page load time'
            ]
        }
    
    async def analyze_chemical_properties(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock chemical properties analysis"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            'analysis': 'Mock chemical properties analysis',
            'predicted_properties': {
                'molecular_weight': 180.16,
                'boiling_point': 178.0,
                'solubility': 'high'
            },
            'safety_assessment': 'Generally safe under normal conditions',
            'research_suggestions': [
                'Test under different pH conditions',
                'Evaluate thermal stability'
            ]
        }

class HTTPLLMService(LLMService):
    """HTTP-based LLM service implementation"""
    
    def __init__(self, api_url: str, api_key: str = None):
        self.api_url = api_url
        self.api_key = api_key
    
    async def extract_chemical_properties(self, chemical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract chemical properties using external LLM API"""
        import httpx
        
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
