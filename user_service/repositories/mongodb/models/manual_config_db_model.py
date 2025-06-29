"""
MongoDB database model for manual configuration.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .youtube_config_db_model import YoutubeConfig


class ManualConfigDBModel(BaseModel):
    """Database model for manual configuration."""

    youtube: YoutubeConfig
