from pydantic_settings import BaseSettings
from pydantic import Field
import logging

class Settings(BaseSettings):
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., alias="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC: str = Field(..., alias="KAFKA_TOPIC")
    KAFKA_GROUP_ID: str = Field(..., alias="KAFKA_GROUP_ID")
    
    # Database Settings
    POSTGRES_DSN: str = Field(..., alias="POSTGRES_DSN")
    
    # LLM Settings
    LLM_API_URL: str = Field(..., alias="LLM_API_URL")
    
    # Celery Settings
    CELERY_BROKER_URL: str = Field(..., alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., alias="CELERY_RESULT_BACKEND")
    
    # Service Settings
    API_PORT: int = Field(8001, alias="API_PORT")
    LOG_LEVEL: str = Field("INFO", alias="LOG_LEVEL")
    
    # Retry Settings
    MAX_RETRIES: int = Field(3, alias="MAX_RETRIES")
    RETRY_DELAY: int = Field(5, alias="RETRY_DELAY")

    class Config:
        env_file = ".env"
        extra = "ignore"

    def setup_logging(self):
        """Configure logging for the application"""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('subscriber_service.log')
            ]
        )

settings = Settings()
settings.setup_logging()
