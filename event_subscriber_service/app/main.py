from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
import asyncio
import logging
from typing import Dict, Any, List

from app.config.settings import settings
from app.infrastructure.postgresql_repository import PostgreSQLRepository
from app.core.event_processing_service import DataAnalyticsService

logger = logging.getLogger(__name__)

# Initialize FastAPI app for monitoring and analytics
app = FastAPI(
    title="Event Subscriber Service",
    description="Monitoring and Analytics API for Event Processing",
    version="1.0.0"
)

# Initialize services
database_repo = PostgreSQLRepository()
analytics_service = DataAnalyticsService(database_repo)

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "event_subscriber"}

@app.get("/api/v1/analytics/user/{user_id}")
async def get_user_analytics(user_id: str):
    """Get analytics summary for a specific user"""
    try:
        summary = await analytics_service.get_user_analytics_summary(user_id)
        return summary
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/researcher/{researcher}")
async def get_researcher_analytics(researcher: str):
    """Get analytics summary for a specific researcher"""
    try:
        summary = await analytics_service.get_researcher_summary(researcher)
        return summary
    except Exception as e:
        logger.error(f"Error getting researcher analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events/user/{user_id}")
async def get_user_events(user_id: str, limit: int = 10):
    """Get recent events for a specific user"""
    try:
        events = await database_repo.get_user_analytics_events(user_id, limit)
        return {"user_id": user_id, "events": events}
    except Exception as e:
        logger.error(f"Error getting user events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events/researcher/{researcher}")
async def get_researcher_events(researcher: str, limit: int = 10):
    """Get recent events for a specific researcher"""
    try:
        events = await database_repo.get_chemical_research_events(researcher, limit)
        return {"researcher": researcher, "events": events}
    except Exception as e:
        logger.error(f"Error getting researcher events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.API_PORT, 
        reload=True
    )
