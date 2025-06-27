from .models import UserAnalyticsEvent, ChemicalResearchEvent

def transform_user_analytics_event(event: UserAnalyticsEvent) -> dict:
    return {
        "type": "user_analytics",
        "user_id": event.user_id,
        "event_type": event.event_type,
        "timestamp": event.timestamp,
        "metadata": event.metadata or {},
    }

def transform_chemical_research_event(event: ChemicalResearchEvent) -> dict:
    return {
        "type": "chemical_research",
        "molecule_id": event.molecule_id,
        "researcher": event.researcher,
        "data": event.data,
        "timestamp": event.timestamp,
    } 