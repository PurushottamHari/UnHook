"""
MongoDB database model for manual configuration.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .youtube_config_db_model import YoutubeConfig

class ManualConfigDBModel(BaseModel):
    """Database model for manual configuration."""
    youtube: YoutubeConfig