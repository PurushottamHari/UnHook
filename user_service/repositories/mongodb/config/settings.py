"""
MongoDB configuration settings.
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# Define the path outside the class
ENV_FILE_PATH = str(Path(__file__).parent.parent.parent.parent / ".env")


class MongoDBSettings(BaseSettings):
    """MongoDB connection settings."""

    # Only MongoDB specific settings
    MONGODB_URI: str
    DATABASE_NAME: str = "youtube_newspaper"
    COLLECTION_NAME: str = "users"

    class Config:
        env_file = ENV_FILE_PATH
        case_sensitive = True
        extra = "ignore"  # This will ignore any extra environment variables


@lru_cache()
def get_mongodb_settings() -> MongoDBSettings:
    """Get cached MongoDB settings."""
    try:
        return MongoDBSettings()
    except Exception as e:
        print(f"Error loading MongoDB settings: {e}")
        print(f"Looking for .env file at: {ENV_FILE_PATH}")
        raise
