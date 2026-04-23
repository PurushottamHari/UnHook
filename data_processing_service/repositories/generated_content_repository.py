"""
Abstract base class for generated content repository.
"""

from abc import ABC, abstractmethod
from typing import Optional

from data_collector_service.models.user_collected_content import ContentType
from data_processing_service.models.generated_content import GeneratedContent


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
    def update_generated_content(
        self, updated_generated_content: GeneratedContent
    ) -> None:
        """Update an existing generated content item."""
        pass
