"""
Models for manual configuration settings.
"""

from typing import List, Dict
from pydantic import BaseModel, Field
from .youtube_config import YoutubeConfig

class ManualConfig(BaseModel):
    youtube: YoutubeConfig 