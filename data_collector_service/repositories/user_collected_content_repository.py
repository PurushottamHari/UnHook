"""
Abstract base class for user collected content repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from data_collector_service.models.user_collected_content import \
    UserCollectedContent


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
    def get_processed_content_with_moderation_passed(
        self, user_id: str
    ) -> List[UserCollectedContent]:
        pass

    @abstractmethod
    def get_unprocessed_content_for_user(
        self, user_id: str
    ) -> List[UserCollectedContent]:
        """
        Get a list of unprocessed collected content for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            List[UserCollectedContent]: List of unprocessed content.
        """
        pass

    @abstractmethod
    def get_content_by_ids(self, content_ids: List[str]) -> List[UserCollectedContent]:
        """
        Get a list of user collected content by their IDs.

        Args:
            content_ids: List of content IDs to fetch.

        Returns:
            List[UserCollectedContent]: List of matching content.
        """
        pass

    @abstractmethod
    def get_content_by_external_id_and_status(
        self, external_id: str, status: ContentStatus
    ) -> List[UserCollectedContent]:
        """
        Get a list of user collected content by external ID and status.

        Args:
            external_id: The external ID of the content.
            status: The status to filter by.

        Returns:
            List[UserCollectedContent]: List of matching content.
        """
        pass

    @abstractmethod
    def get_content_by_external_id(
        self, user_id: str, external_id: str
    ) -> Optional[UserCollectedContent]:
        """
        Get a user collected content by user ID and external ID.

        Args:
            user_id: The ID of the user.
            external_id: The external ID of the content.

        Returns:
            Optional[UserCollectedContent]: The matching content or None.
        """
        pass

    @abstractmethod
    def upsert_user_collected_content_batch(
        self, user_collected_content_list: List[UserCollectedContent]
    ) -> None:
        """
        Batch upsert UserCollectedContent items.
        Matches by user_id and external_id.

        Args:
            user_collected_content_list: The list of content to upsert.
        """
        pass
