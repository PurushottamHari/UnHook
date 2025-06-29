from collections import UserDict
from datetime import datetime
from typing import Dict, List, Optional

from .subtitles import Subtitles


class YouTubeVideoDetails:
    """Model class for storing YouTube video details."""

    def __init__(
        self,
        video_id: str,
        title: str,
        channel_name: str,
        views: int,
        description: str,
        thumbnail: str,
        channel_id: Optional[str] = None,
        release_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        language: Optional[str] = None,
        duration_in_seconds: Optional[int] = None,
        comments_count: Optional[int] = None,
        likes_count: Optional[int] = None,
        subtitles: Optional[Subtitles] = None,
    ):
        self.video_id = video_id
        self.title = title
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.release_date = release_date
        self.views = views
        self.description = description
        self.thumbnail = thumbnail
        self.created_at = created_at or datetime.utcnow()
        self.tags = tags
        self.categories = categories
        self.language = language
        self.duration_in_seconds = duration_in_seconds
        self.comments_count = comments_count
        self.likes_count = likes_count
        self.subtitles = subtitles

    def to_dict(self) -> dict:
        """Convert the model instance to a dictionary."""
        result = {
            "video_id": self.video_id,
            "title": self.title,
            "channel_name": self.channel_name,
            "channel_id": self.channel_id,
            "views": self.views,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "categories": self.categories,
            "language": self.language,
            "duration_in_seconds": self.duration_in_seconds,
            "comments_count": self.comments_count,
            "likes_count": self.likes_count,
        }
        if self.release_date:
            result["release_date"] = self.release_date.isoformat()
        if self.subtitles:
            result["subtitles"] = self.subtitles.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "YouTubeVideoDetails":
        """Create a model instance from a dictionary."""
        return cls(
            video_id=data["video_id"],
            title=data["title"],
            channel_id=data.get("channel_id"),
            channel_name=data["channel_name"],
            views=data["views"],
            description=data["description"],
            thumbnail=data["thumbnail"],
            release_date=(
                datetime.fromisoformat(data["release_date"])
                if data.get("release_date")
                else None
            ),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else None
            ),
            tags=data.get("tags"),
            categories=data.get("categories"),
            language=data.get("language"),
            duration_in_seconds=data.get("duration_in_seconds"),
            comments_count=data.get("comments_count"),
            likes_count=data.get("likes_count"),
            subtitles=(
                Subtitles.from_dict(data["subtitles"]) if "subtitles" in data else None
            ),
        )
