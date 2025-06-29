"""
Abstract base class for user collected content repository.
"""

from abc import ABC, abstractmethod
from typing import List

from data_collector_service.models.user_collected_content import UserCollectedContent


class UserCollectedContentRepository(ABC):
    """Abstract base class for managing user collected content data."""

    @abstractmethod
    def filter_already_collected_content(
        self, user_id: str, video_ids: List[str]
    ) -> List[str]:
        """
        Get list of Content IDs that haven't been collected yet for a user.

        Args:
            user_id: The ID of the user
            video_ids: List of video IDs to check

        Returns:
            List[str]: List of uncollected video IDs
        """
        pass

    @abstractmethod
    def add_collected_videos(self, videos: List[dict]) -> None:
        """
        Add collected videos to the user's history.

        Args:
            videos: List of collected video information
        """
        pass

    @abstractmethod
    def get_processed_content_with_moderation_passed(
        self, user_id: str
    ) -> List[UserCollectedContent]:
        pass
