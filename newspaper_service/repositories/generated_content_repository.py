"""
Abstract base class for generated content repository.
"""

from abc import ABC, abstractmethod
from typing import List

from data_processing_service.models.generated_content import GeneratedContent
from user_service.models.enums import CategoryName


class GeneratedContentRepository(ABC):
    """Abstract base class for managing generated content data."""

    @abstractmethod
    def filter_external_ids_by_category(
        self, external_ids: List[str], categories: List[CategoryName]
    ) -> List[str]:
        """
        Filter external IDs by categories, returning only those that have generated content
        with the specified categories and ARTICLE_GENERATED status.

        Args:
            external_ids: List of external IDs to filter
            categories: List of categories to match against

        Returns:
            List[str]: List of external IDs that match the criteria
        """
        pass

    @abstractmethod
    def get_content_by_id(self, content_id: str) -> GeneratedContent:
        """
        Fetch a single GeneratedContent object by MongoDB _id.

        Args:
            content_id: MongoDB _id to fetch

        Returns:
            GeneratedContent: Generated content object or None if not found
        """
        pass

    @abstractmethod
    def get_content_by_external_id(self, external_id: str) -> GeneratedContent:
        """
        Fetch a single GeneratedContent object by external_id.

        Args:
            external_id: External ID to fetch

        Returns:
            GeneratedContent: Generated content object or None if not found
        """
        pass

    @abstractmethod
    def get_reading_times_by_external_ids(self, external_ids: List[str]) -> dict:
        """
        Fetch reading times for multiple external IDs efficiently.

        Args:
            external_ids: List of external IDs to fetch reading times for

        Returns:
            dict: Dictionary mapping external_id to reading_time_seconds
        """
        pass

    @abstractmethod
    def get_contents_by_external_ids(self, external_ids: List[str]) -> List[GeneratedContent]:
        """
        Fetch multiple GeneratedContent objects by external_ids.

        Args:
            external_ids: List of external IDs to fetch

        Returns:
            List[GeneratedContent]: List of generated content objects with ARTICLE_GENERATED status
        """
        pass
