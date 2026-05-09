"""
Service for handling generated content business logic.
"""

import logging
from typing import Optional, Tuple

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.user_collected_content import \
    UserCollectedContent
from data_processing_service.models.generated_content import GeneratedContent

from ..external.user_service import UserServiceClient
from ..repositories.generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from ..repositories.generated_content_repository import \
    GeneratedContentRepository
from ..repositories.user_collected_content_repository import \
    UserCollectedContentRepository


@injectable()
class GeneratedContentService:
    """Service for handling generated content business logic."""

    @inject
    def __init__(
        self,
        generated_content_repository: GeneratedContentRepository,
        user_collected_content_repository: UserCollectedContentRepository,
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
        self._interaction_repository = interaction_repository
        self._user_service_client = user_service_client
        self.logger = logging.getLogger(__name__)

    async def get_generated_content_by_id(
        self, content_id: str
    ) -> Tuple[GeneratedContent, UserCollectedContent]:
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
        user_collected_content = (
            self._user_collected_content_repository.get_content_by_external_id(
                content.external_id
            )
        )
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        return content, user_collected_content
