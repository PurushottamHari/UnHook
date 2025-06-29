"""
Models for manual configuration settings.
"""

from typing import Dict, List

from pydantic import BaseModel, Field

from .youtube_config import YoutubeConfig


class ManualConfig(BaseModel):
    youtube: YoutubeConfig
