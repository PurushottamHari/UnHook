from abc import ABC, abstractmethod
from typing import List

from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoDetails


class YouTubeCollectedContentRepository(ABC):
    """Abstract base class for managing raw YouTube collected content data."""

    @abstractmethod
    def upsert_videos(self, videos: List[YouTubeVideoDetails]) -> None:
        """
        Add or update YouTube videos in the shared collection.

        Args:
            videos: List of YouTubeVideoDetails objects to store
        """
        pass

    @abstractmethod
    def get_video_by_id(self, video_id: str) -> YouTubeVideoDetails:
        """
        Retrieve a YouTube video by its ID.

        Args:
            video_id: The YouTube video ID

        Returns:
            YouTubeVideoDetails: The video details or None if not found
        """
        pass

    @abstractmethod
    def get_videos_by_ids(self, video_ids: List[str]) -> List[YouTubeVideoDetails]:
        """
        Retrieve multiple YouTube videos by their IDs.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            List[YouTubeVideoDetails]: List of matching video details
        """
        pass

    @abstractmethod
    def filter_existing_videos(self, video_ids: List[str]) -> List[str]:
        """
        Get list of video IDs that haven't been added to the shared collection yet.

        Args:
            video_ids: List of video IDs to check

        Returns:
            List[str]: List of uncollected video IDs
        """
        pass
