import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fleet Route Optimization API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    class Config:
        case_sensitive = True

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)