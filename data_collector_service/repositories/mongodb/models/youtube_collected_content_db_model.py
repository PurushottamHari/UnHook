from typing import Any, List, Optional

from pydantic import BaseModel, Field

from data_collector_service.repositories.mongodb.models.subtitle_db_model import \
    SubtitleDB


class YouTubeVideoStatusDetailDB(BaseModel):
    """Database model for YouTube video status updates."""

    status: str
    created_at: float
    reason: str = ""


class YouTubeCollectedContentDBModel(BaseModel):
    """Database model for storing YouTube video details in MongoDB."""

    id: str = Field(alias="_id")  # video_id will be the _id
    video_id: str
    title: str
    channel_id: Optional[str] = None
    channel_name: str
    views: int
    description: Optional[str] = None
    thumbnail: str
    status: str
    status_details: List[YouTubeVideoStatusDetailDB]
    release_date: Optional[float] = None
    created_at: float
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    language: Optional[str] = None
    duration_in_seconds: Optional[int] = None
    comments_count: Optional[int] = None
    likes_count: Optional[int] = None
    subtitles: Optional[SubtitleDB] = None
    version: int = Field(default=1)

    class Config:
        """Pydantic config."""

        populate_by_name = True
