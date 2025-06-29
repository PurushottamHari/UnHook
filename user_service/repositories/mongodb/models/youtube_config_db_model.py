from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .interests_db_model import NotInterestedDBModel


class YoutubeChannelConfig(BaseModel):
    channel_id: str
    max_videos_daily: int
    output_type: str
    not_interested: Optional[List[NotInterestedDBModel]] = None


class YoutubeConfig(BaseModel):
    discover_on: List[str]
    channels: List[YoutubeChannelConfig]
