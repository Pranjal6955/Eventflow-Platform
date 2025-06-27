from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from app.api.routes import router as api_router
from app.config.settings import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Event Publisher Service", 
    description="High-performance event publishing platform with Kafka integration",
    version="1.0.0",
    openapi_url=f"{settings.API_BASE_PATH}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

app.include_router(api_router, prefix=settings.API_BASE_PATH)

@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "event_publisher", "version": "1.0.0"}

@app.get("/metrics")
def get_metrics():
    """Basic metrics endpoint"""
    return {
        "service": "event_publisher",
        "status": "running",
        "version": "1.0.0",
        "uptime": "N/A"  # Would implement actual uptime tracking
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.API_PORT, 
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
