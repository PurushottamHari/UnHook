"""
Service for handling generated content business logic.
"""

import logging
from typing import List, Optional

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models import ContentType
from data_collector_service.models.user_collected_content import UserCollectedContent
from data_collector_service.models.youtube.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_processing_service.models.generated_content import GeneratedContent
from fastapi import HTTPException
from injector import inject

from ..api.adaptors.newspaper_v2_adaptor import NewspaperV2Adaptor
from ..api.models.article_response import ArticleResponse
from ..external.user_service import UserServiceClient
from ..repositories.generated_content_interaction_repository import (
    GeneratedContentInteractionRepository,
)
from ..repositories.generated_content_repository import GeneratedContentRepository
from ..repositories.user_collected_content_repository import (
    UserCollectedContentRepository,
)
from ..repositories.youtube_collected_content_repository import (
    YouTubeCollectedContentRepository,
)


@injectable()
class GeneratedContentService:
    """Service for handling generated content business logic."""

    @inject
    def __init__(
        self,
        generated_content_repository: GeneratedContentRepository,
        user_collected_content_repository: UserCollectedContentRepository,
        youtube_collected_content_repository: YouTubeCollectedContentRepository,
        interaction_repository: GeneratedContentInteractionRepository,
        user_service_client: UserServiceClient,
    ):
        """
        Initialize the service.

        Args:
            generated_content_repository: Repository for generated content operations
            user_collected_content_repository: Repository for user collected content operations
            interaction_repository: Repository for interaction operations
            user_service_client: Client for user service operations
        """
        self._generated_content_repository = generated_content_repository
        self._user_collected_content_repository = user_collected_content_repository
        self._youtube_collected_content_repository = (
            youtube_collected_content_repository
        )
        self._interaction_repository = interaction_repository
        self._user_service_client = user_service_client
        self.logger = logging.getLogger(__name__)

    async def get_generated_content_by_id(
        self, user_id: str, content_id: str
    ) -> ArticleResponse:
        """
        Get generated content by its MongoDB _id and return it with its external_id.

        Args:
            content_id: MongoDB _id of the generated content

        Returns:
            Tuple[GeneratedContent, str]: The generated content object and its external_id.

        Raises:
            ValueError: If content not found
        """
        content = self._generated_content_repository.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=404, detail=f"Content not found: {content_id}"
            )

        source_details = None
        if content.content_type == ContentType.YOUTUBE_VIDEO:
            source_details = self._youtube_collected_content_repository.get_video_by_id(
                content.external_id
            )

        # Fetch interactions for this content and user
        interactions_map = self._interaction_repository.get_active_interactions_by_generated_content_ids(
            user_id=user_id, generated_content_ids=[content_id]
        )
        interactions = interactions_map.get(content_id, [])

        return NewspaperV2Adaptor.to_article_response_from_youtube(
            content=content,
            youtube_details=source_details,
            interactions=interactions,
        )
