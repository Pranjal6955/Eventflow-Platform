from pydantic import BaseModel, Field
from typing import Optional

class UserAnalyticsEvent(BaseModel):
    user_id: str
    event_type: str
    timestamp: str
    metadata: Optional[dict] = None

class ChemicalResearchEvent(BaseModel):
    molecule_id: str
    researcher: str
    data: dict
    timestamp: str 