from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID

class DatabaseRepository(ABC):
    """Abstract base repository for database operations"""
    
    @abstractmethod
    async def save_user_analytics_event(self, event_data: Dict[str, Any]) -> UUID:
        pass
    
    @abstractmethod
    async def save_chemical_research_event(self, event_data: Dict[str, Any]) -> UUID:
        pass
    
    @abstractmethod
    async def get_user_analytics_events(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_chemical_research_events(self, researcher: str, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def update_event_processing_status(self, event_id: UUID, status: str, error_message: Optional[str] = None):
        pass
    
    @abstractmethod
    async def create_event_processing_status(self, event_id: UUID, event_type: str) -> UUID:
        pass
