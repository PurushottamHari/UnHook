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

    async def transition_to_processed(self, user_id: str, external_id: str) -> None:
        """
        Transition user collected content status to PROCESSED.
        """
        logger.info(
            f"🔄 Transitioning content {external_id} for user {user_id} to PROCESSED"
        )

        # 1. Fetch user collected content
        content = self.user_content_repository.get_content_by_external_id(
            user_id, external_id
        )
        if not content:
            error_msg = f"User collected content for external ID {external_id} and user {user_id} not found"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        # 2. Check status
        if content.status == ContentStatus.PROCESSING:
            logger.info(f"Processing content in status {content.status}: {content.id}")

            # Deep copy as requested
            content_clone = deepcopy(content)

            content_clone.set_status(
                ContentStatus.PROCESSED, "Article generation completed successfully"
            )
            content_clone.version += 1

            # Update repository
            self.user_content_repository.upsert_user_collected_content_batch(
                [content_clone]
            )
            logger.info(
                f"✅ Content {content_clone.id} moved to PROCESSED status (version {content_clone.version})"
            )

        elif content.status == ContentStatus.PROCESSED:
            logger.info(
                f"⏭️ Content {content.id} is already in PROCESSED status. Ignoring."
            )

        else:
            error_msg = (
                f"Cannot transition content in status {content.status} to PROCESSED. "
                "Expected PROCESSING or PROCESSED."
            )
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        # Raise event
        ready_event = UserCollectedContentReadyToBeUsedEvent(
            payload=UserCollectedContentReadyToUsedPayload(
                user_id=user_id,
                user_collected_content_id=content_clone.id,
                external_id=external_id,
            )
        )

        await self.message_producer.publish_event(ready_event.topic, ready_event)
        logger.info(
            f"📤 Published UserCollectedContentReadyToBeUsedEvent for {content_clone.id}"
        )
