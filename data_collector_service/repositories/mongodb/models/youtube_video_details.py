from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from data_collector_service.repositories.mongodb.models.subtitle_db_model import (
    SubtitleDB,
)


class YouTubeVideoDetailsDB(BaseModel):
    """Model class for storing YouTube video details in MongoDB."""

    id: Optional[Any] = Field(None, alias="_id")
    video_id: str
    title: str
    channel_id: Optional[str] = None
    channel_name: str
    views: int
    description: str
    thumbnail: str
    release_date: Optional[float] = None
    created_at: float
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    language: Optional[str] = None
    duration_in_seconds: Optional[int] = None
    comments_count: Optional[int] = None
    likes_count: Optional[int] = None
    subtitles: Optional[SubtitleDB] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True
