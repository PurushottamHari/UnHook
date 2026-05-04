import logging
from copy import deepcopy

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.events.data_collector_service.models import (
    UserCollectedContentReadyToBeUsedEvent,
    UserCollectedContentReadyToUsedPayload)
from data_collector_service.config.config import Config
from data_collector_service.models.user_collected_content import ContentStatus
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository

logger = logging.getLogger(__name__)


@injectable()
class TransitionUserCollectedContentStatusToProcessedService:
    """Service for transitioning UserCollectedContent status to PROCESSED."""

    @inject
    def __init__(
        self,
        user_content_repository: UserCollectedContentRepository,
        message_producer: MessageProducer,
        config: Config,
    ):
        self.user_content_repository = user_content_repository
        self.message_producer = message_producer
        self.config = config

    async def transition_to_processed(
        self, external_id: str, user_id: str = None
    ) -> None:
        """
        Transition all user collected content for a given external_id to PROCESSED.
        """
        logger.info(
            f"🔄 Transitioning all content for external_id {external_id} to PROCESSED"
        )

        # 1. Fetch all user collected content in PROCESSING status for this external_id
        contents_to_process = (
            self.user_content_repository.get_content_by_external_id_and_status(
                external_id, ContentStatus.PROCESSING
            )
        )

        if not contents_to_process:
            logger.info(
                f"⏭️ No content in PROCESSING status found for external_id {external_id}. Ignoring."
            )
            return

        processed_contents = []
        events_to_publish = []

        for content in contents_to_process:
            logger.info(
                f"Processing content {content.id} for user {content.user_id} in status {content.status}"
            )

            # Deep copy as requested
            content_clone = deepcopy(content)

            content_clone.set_status(
                ContentStatus.PROCESSED, "Article generation completed successfully"
            )
            content_clone.version += 1

            processed_contents.append(content_clone)

            # Prepare event
            ready_event = UserCollectedContentReadyToBeUsedEvent(
                payload=UserCollectedContentReadyToUsedPayload(
                    user_id=content_clone.user_id,
                    user_collected_content_id=content_clone.id,
                    external_id=external_id,
                )
            )
            events_to_publish.append(ready_event)

        # 2. Update repository in batch
        if processed_contents:
            self.user_content_repository.upsert_user_collected_content_batch(
                processed_contents
            )
            logger.info(
                f"✅ Successfully transitioned {len(processed_contents)} content items to PROCESSED status"
            )

        # 3. Raise events in one shot
        if events_to_publish:
            await self.message_producer.publish_events(events_to_publish)
            logger.info(
                f"📤 Published {len(events_to_publish)} UserCollectedContentReadyToBeUsedEvent(s) in one shot"
            )
