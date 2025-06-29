"""
Models for YouTube configuration settings.
"""

from typing import List

from pydantic import BaseModel, Field

from .enums import OutputType, Weekday
from .interests import NotInterested


class YoutubeChannelConfig(BaseModel):
    channel_id: str = Field(..., min_length=1)
    max_videos_daily: int = Field(..., gt=0)
    output_type: OutputType
    not_interested: List[NotInterested] = Field(default_factory=list)


class YoutubeConfig(BaseModel):
    discover_on: List[Weekday]
    channels: List[YoutubeChannelConfig]
