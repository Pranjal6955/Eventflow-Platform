from pydantic_settings import BaseSettings
from pydantic import Field
import logging

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = Field(..., alias="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC: str = Field(..., alias="KAFKA_TOPIC")
    API_PORT: int = Field(8000, alias="API_PORT")
    API_BASE_PATH: str = Field("/api/v1", alias="API_BASE_PATH")
    
    # Additional settings for enhanced functionality
    LOG_LEVEL: str = Field("INFO", alias="LOG_LEVEL")
    MAX_RETRIES: int = Field(3, alias="MAX_RETRIES")
    RETRY_DELAY: int = Field(5, alias="RETRY_DELAY")
    ENABLE_METRICS: bool = Field(True, alias="ENABLE_METRICS")

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
                logging.FileHandler('publisher_service.log')
            ]
        )

settings = Settings()
settings.setup_logging()