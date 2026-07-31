from abc import ABC, abstractmethod
from typing import List, Optional

from data_collector_service.models.webpage.webpage_collected_content import \
    WebpageCollectedContent


class WebpageCollectedContentRepository(ABC):
    """Abstract base class for managing webpage collected content data."""

    @abstractmethod
    def upsert_webpages(self, webpages: List[WebpageCollectedContent]) -> None:
        """
        Add or update webpages in the collection.

        Args:
            webpages: List of WebpageCollectedContent objects to store
        """
        pass

    @abstractmethod
    def get_webpage_by_id(self, id: str) -> WebpageCollectedContent:
        """
        Retrieve a webpage by its ID.

        Args:
            id: The webpage UUID

        Returns:
            WebpageCollectedContent: The webpage details or None if not found
        """
        pass

    @abstractmethod
    def get_webpages_by_ids(self, ids: List[str]) -> List[WebpageCollectedContent]:
        """
        Retrieve multiple webpages by their IDs.

        Args:
            ids: List of webpage UUIDs

        Returns:
            List[WebpageCollectedContent]: List of matching webpage details
        """
        pass

    @abstractmethod
    def filter_existing_webpages(self, shas: List[str]) -> List[str]:
        """
        Get list of SHA hashes that haven't been added to the collection yet.

        Args:
            shas: List of SHA hashes to check

        Returns:
            List[str]: List of SHA hashes that don't exist in the collection
        """
        pass

    @abstractmethod
    def get_webpage_by_sha(self, sha: str) -> Optional[WebpageCollectedContent]:
        """
        Retrieve a webpage by its SHA hash.

        Args:
            sha: The webpage SHA hash

        Returns:
            WebpageCollectedContent: The webpage details or None if not found
        """
        pass
