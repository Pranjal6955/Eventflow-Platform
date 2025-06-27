from fastapi import APIRouter, Depends, HTTPException, status
from .models import UserAnalyticsEvent, ChemicalResearchEvent
from .transformers import transform_user_analytics_event, transform_chemical_research_event
from app.core.event_service import EventService, get_event_service

router = APIRouter()

@router.post("/events/analytics", status_code=202)
def publish_user_analytics_event(
    event: UserAnalyticsEvent,
    event_service: EventService = Depends(get_event_service),
):
    try:
        payload = transform_user_analytics_event(event)
        event_service.publish_event(payload)
        return {"message": "Event published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/chemical", status_code=202)
def publish_chemical_research_event(
    event: ChemicalResearchEvent,
    event_service: EventService = Depends(get_event_service),
):
    try:
        payload = transform_chemical_research_event(event)
        event_service.publish_event(payload)
        return {"message": "Event published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 