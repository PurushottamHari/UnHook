"""
MongoDB settings configuration for newspaper service.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

# Match env loading behavior of other services: read .env from service root
ENV_FILE_PATH = str(Path(__file__).parent.parent.parent.parent / ".env")


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    # Prefer MONGODB_URI (consistent with other services); allow MONGODB_URL as fallback
    MONGODB_URI: Optional[str] = None
    MONGODB_URL: Optional[str] = None
    # Must match the DB used by data_collector_service to read collected content
    DATABASE_NAME: str = "youtube_newspaper"
    USER_COLLECTED_CONTENT_COLLECTION_NAME: str = "collected_content"
    NEWSPAPER_COLLECTION_NAME: str = "newspapers"
    GENERATED_CONTENT_INTERACTION_COLLECTION_NAME: str = "generated_content_interactions"

    class Config:
        env_file = ENV_FILE_PATH
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_mongodb_settings() -> DatabaseSettings:
    """Get cached MongoDB settings."""
    return DatabaseSettings()
