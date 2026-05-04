"""
Service for starting the data processing flow for user collected content.
"""

import logging

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentType)
from data_processing_service.external.user_service.client import \
    UserServiceClient
from data_processing_service.repositories.user_content_repository import \
    UserContentRepository
from data_processing_service.services.processing.youtube.generate_required_content.generate_required_content_for_youtube_service import \
    GenerateRequiredContentForYoutubeService


@injectable()
class StartDataProcessingService:
    """Service for orchestrating the start of data processing for user collected content."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        user_content_repository: UserContentRepository,
        youtube_generation_service: GenerateRequiredContentForYoutubeService,
        message_producer: MessageProducer,
    ):
        """
        Initialize the service with dependencies.
        """
        self.user_service_client = user_service_client
        self.user_content_repository = user_content_repository
        self.youtube_generation_service = youtube_generation_service
        self.message_producer = message_producer
        self.logger = logging.getLogger(__name__)

    async def start_processing(self, user_id: str, user_collected_content_id: str):
        """
        Start the data processing flow.
        1. Fetch user.
        2. Fetch user collected content.
        3. Verify status.
        4. Generate required content.
        5. Publish next command.
        """
        self.logger.info(
            f"🚀 Starting data processing for user_id: {user_id}, content_id: {user_collected_content_id}"
        )

        # 1. Fetch user
        user = await self.user_service_client.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # 2. Fetch user collected content
        content = self.user_content_repository.get_user_collected_content_by_id(
            user_id=user_id, content_id=user_collected_content_id
        )
        if not content:
            raise ValueError(
                f"User collected content not found: {user_collected_content_id}"
            )

        # 3. Verify status
        if content.status != ContentStatus.PROCESSING:
            raise ValueError(
                f"Content {user_collected_content_id} is not in PROCESSING status. "
                f"Current status: {content.status}"
            )

        # 4. Based on content type, generate required content
        generated_content_id = None
        if content.content_type == ContentType.YOUTUBE_VIDEO:
            generated_content_id = (
                await self.youtube_generation_service.generate_required_content(
                    user_collected_content=content
                )
            )
        else:
            raise NotImplementedError(
                f"Processing for content type {content.content_type} is not implemented yet."
            )
