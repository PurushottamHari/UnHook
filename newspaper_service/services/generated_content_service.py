"""
Service for handling generated content business logic.
"""

import logging
from typing import Optional

from data_processing_service.models.generated_content import GeneratedContent

from ..models.generated_content_list import (
    GeneratedContentListData, GeneratedContentListResponse)
from ..repositories.generated_content_repository import GeneratedContentRepository
from ..repositories.newspaper_repository import NewspaperRepository
from ..repositories.user_collected_content_repository import \
    UserCollectedContentRepository


class GeneratedContentService:
    """Service for handling generated content business logic."""

    def __init__(
        self,
        generated_content_repository: GeneratedContentRepository,
        newspaper_repository: NewspaperRepository,
        user_collected_content_repository: UserCollectedContentRepository,
    ):
        """
        Initialize the service.

        Args:
            generated_content_repository: Repository for generated content operations
            newspaper_repository: Repository for newspaper operations
            user_collected_content_repository: Repository for user collected content operations
        """
        self._generated_content_repository = generated_content_repository
        self._newspaper_repository = newspaper_repository
        self._user_collected_content_repository = user_collected_content_repository
        self.logger = logging.getLogger(__name__)

    async def get_generated_content_by_id(
        self, content_id: str
    ) -> GeneratedContent:
        """
        Get generated content by its ID (external_id).

        Args:
            content_id: External ID of the generated content

        Returns:
            GeneratedContent: The generated content object

        Raises:
            ValueError: If content not found
        """
        content = self._generated_content_repository.get_content_by_external_id(
            content_id
        )
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        return content

    async def list_generated_content_for_newspaper(
        self,
        newspaper_id: str,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> GeneratedContentListResponse:
        """
        List generated content for a specific newspaper with pagination.

        Args:
            newspaper_id: ID of the newspaper
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return (default=10, max=10)

        Returns:
            Paginated list response with content and hasNext flag

        Raises:
            ValueError: If newspaper not found or page_limit exceeds maximum
        """
        # Validate page_limit
        if page_limit <= 0:
            raise ValueError("page_limit must be greater than 0")
        if page_limit > 10:
            raise ValueError("page_limit cannot exceed 10")

        # Get newspaper by ID
        newspaper = self._newspaper_repository.get_newspaper(newspaper_id)
        if not newspaper:
            raise ValueError(f"Newspaper not found: {newspaper_id}")

        # Extract user_collected_content_id values from considered_content_list
        considered_content_ids = [
            item.user_collected_content_id
            for item in newspaper.considered_content_list
        ]

        # If no considered content, return empty response
        if not considered_content_ids:
            return GeneratedContentListResponse(
                data=GeneratedContentListData(
                    list_response=[],
                    hasNext=False,
                )
            )

        # Fetch UserCollectedContent objects by IDs (single batch call)
        user_collected_contents = (
            self._user_collected_content_repository.get_contents_by_ids(
                considered_content_ids
            )
        )

        # Extract external_id values from fetched UserCollectedContent objects
        external_ids = [
            content.external_id
            for content in user_collected_contents
            if content.external_id
        ]

        # Filter out None/empty external_ids
        external_ids = [eid for eid in external_ids if eid]

        # If no external_ids, return empty response
        if not external_ids:
            return GeneratedContentListResponse(
                data=GeneratedContentListData(
                    list_response=[],
                    hasNext=False,
                )
            )

        # Sort external_ids alphabetically for consistent ordering
        external_ids.sort()

        # Paginate external_ids list
        start_index = 0
        if starting_after:
            try:
                start_index = external_ids.index(starting_after) + 1
            except ValueError:
                # starting_after not found, start from beginning
                start_index = 0

        # Get page_limit + 1 items to determine hasNext
        paginated_external_ids = external_ids[start_index : start_index + page_limit + 1]
        has_next = len(paginated_external_ids) > page_limit

        # Take only first page_limit items for actual results
        external_ids_to_fetch = paginated_external_ids[:page_limit]

        # If no external_ids to fetch, return empty response
        if not external_ids_to_fetch:
            return GeneratedContentListResponse(
                data=GeneratedContentListData(
                    list_response=[],
                    hasNext=False,
                )
            )

        # Fetch GeneratedContent objects for paginated external_ids
        generated_contents = self._generated_content_repository.get_contents_by_external_ids(
            external_ids_to_fetch
        )

        # Create mapping dict for efficient collation
        content_map = {content.external_id: content for content in generated_contents}

        # Collate results: match GeneratedContent objects back to paginated external_ids order
        collated_contents = [
            content_map[external_id]
            for external_id in external_ids_to_fetch
            if external_id in content_map
        ]

        return GeneratedContentListResponse(
            data=GeneratedContentListData(
                list_response=collated_contents,
                hasNext=has_next,
            )
        )

        # The complication is due to a bug here, the newspaper should directly contain the generated content ids

