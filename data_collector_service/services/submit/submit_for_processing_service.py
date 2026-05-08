import logging
from typing import Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.commands.data_processing_service.models import (
    StartDataProcessingForUserCollectedContentCommand,
    StartDataProcessingForUserCollectedContentPayload)
from data_collector_service.config.config import Config
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentSubStatus, ContentType, UserCollectedContent)
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from data_collector_service.services.submit.youtube.submit_youtube_content_for_processing_service import \
    SubmitYoutubeContentForProcessingService

logger = logging.getLogger(__name__)


@injectable()
class SubmitForProcessingService:
    """Service for submitting moderated content for further processing."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        user_content_repository: UserCollectedContentRepository,
        submit_youtube_content_for_processing_service: SubmitYoutubeContentForProcessingService,
        message_producer: MessageProducer,
    ):
        self.user_service_client = user_service_client
        self.user_content_repository = user_content_repository
        self.submit_youtube_content_for_processing_service = (
            submit_youtube_content_for_processing_service
        )
        self.message_producer = message_producer

    async def submit_for_processing(
        self, user_id: str, user_collected_content_id: str
    ) -> None:
        """
        Process a single user collected content entry and move it to processing status.
        """
        logger.info(
            f"🎬 [SubmitForProcessingService] Submitting content {user_collected_content_id} for user {user_id}"
        )

        # 1. Fetch and validate user
        user = await self.user_service_client.get_user(user_id)
        if not user:
            error_msg = f"User {user_id} not found"
            logger.error(f"❌ [SubmitForProcessingService] {error_msg}")
            raise ValueError(error_msg)

        # 2. Fetch user collected content
        content_list = self.user_content_repository.get_content_by_ids(
            [user_collected_content_id]
        )
        if not content_list:
            error_msg = f"Content {user_collected_content_id} not found"
            logger.error(f"❌ [SubmitForProcessingService] {error_msg}")
            raise ValueError(error_msg)

        content = content_list[0]

        # 3. Check status
        if content.status == ContentStatus.ACCEPTED:
            logger.info(f"Processing ACCEPTED content: {content.id}")

            if content.content_type == ContentType.YOUTUBE_VIDEO:
                await self.submit_youtube_content_for_processing_service.process_youtube_subtitles(
                    content
                )

            content.set_status(
                ContentStatus.PROCESSING, "Moderated content submitted for processing"
            )
            content.version += 1

            # Update repository
            self.user_content_repository.upsert_user_collected_content_batch([content])
            logger.info(
                f"✅ Content {content.id} moved to PROCESSING status (version {content.version})"
            )

        elif content.status == ContentStatus.PROCESSING:
            logger.info(
                f"⏭️ Content {content.id} is already in PROCESSING status. Ignoring."
            )

        else:
            error_msg = f"Cannot submit content in status {content.status}. Expected ACCEPTED or PROCESSING."
            logger.error(f"❌ [SubmitForProcessingService] {error_msg}")
            raise ValueError(error_msg)

        # 4. Publish command to Start Data Processing Service
        payload = StartDataProcessingForUserCollectedContentPayload(
            user_id=user_id,
            user_collected_content_id=user_collected_content_id,
        )
        command = StartDataProcessingForUserCollectedContentCommand(payload=payload)

        await self.message_producer.send_command(command=command)

        logger.info(
            f"✅ [SubmitForProcessingService] Submitted content {user_collected_content_id} to data_processing_service"
        )
