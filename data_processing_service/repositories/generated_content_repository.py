"""
Abstract base class for generated content repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentType)
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)


class GeneratedContentRepository(ABC):
    """Abstract base class for managing generated content data."""

    @abstractmethod
    def add_generated_content(self, generated_content: GeneratedContent) -> None:
        """Add a new generated content item."""
        pass

    @abstractmethod
    def get_generated_content_by_external_id(
        self, external_id: str, content_type: ContentType
    ) -> Optional[GeneratedContent]:
        """Get generated content by its external ID and content type."""
        pass

    @abstractmethod
    def get_generated_content(
        self,
        status: GeneratedContentStatus,
        content_type: ContentType,
    ) -> List[GeneratedContent]:
        """Get list of generated content with the given status and content_type."""
        pass

    @abstractmethod
    def get_generated_content_by_ids(
        self,
        content_ids: List[str],
    ) -> List[GeneratedContent]:
        """Get list of generated content with the given IDs."""
        pass

    @abstractmethod
    def get_generated_content_by_user_collected_content_status(
        self,
        user_id: str,
        status: GeneratedContentStatus,
        content_type: ContentType,
        user_collected_content_status: ContentStatus,
    ) -> List[GeneratedContent]:
        """
        Get list of generated content with the given status and content_type,
        filtered by the status of the associated user collected content for a specific user.
        """
        pass

    @abstractmethod
    def update_generated_content(
        self, updated_generated_content: GeneratedContent
    ) -> None:
        """Update an existing generated content item."""
        pass

    @abstractmethod
    def update_generated_content_batch(
        self, updated_generated_content_list: List[GeneratedContent]
    ) -> None:
        """Update a batch of generated content items."""
        pass
