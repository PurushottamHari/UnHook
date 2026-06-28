from abc import ABC, abstractmethod
from typing import List, Optional

from data_collector_service.models.youtube.youtube_video_details import (
    YouTubeVideoDetails,
)


class YouTubeCollectedContentRepository(ABC):
    @abstractmethod
    def get_video_by_id(self, video_id: str) -> Optional[YouTubeVideoDetails]:
        """Retrieve a YouTube video by its ID."""
        pass

    @abstractmethod
    def get_videos_by_ids(self, video_ids: List[str]) -> List[YouTubeVideoDetails]:
        """Retrieve multiple YouTube videos by their IDs."""
        pass
