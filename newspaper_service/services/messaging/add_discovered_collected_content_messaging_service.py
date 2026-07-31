import logging

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.commands.data_collector_service.models import (
    AddDiscoveredCollectedContentCommand, AddDiscoveredCollectedContentPayload)
from user_service.models.enums import CategoryName


@injectable()
class AddDiscoveredCollectedContentMessagingService:
    """Service to publish an AddDiscoveredCollectedContent command via Redis."""

    @inject
    def __init__(self, message_producer: MessageProducer):
        self.message_producer = message_producer
        self.logger = logging.getLogger(__name__)

    async def execute(self, payload: AddDiscoveredCollectedContentPayload) -> None:
        """
        Validates and publishes an AddDiscoveredCollectedContentCommand.
        """
        self.logger.info(
            f"Publishing AddDiscoveredCollectedContentCommand for user {payload.user_id}"
        )

        _validate_payload(payload)

        command = AddDiscoveredCollectedContentCommand(payload=payload)

        await self.message_producer.send_command(command)
        self.logger.info(
            f"Successfully published AddDiscoveredCollectedContentCommand for user {payload.user_id}"
        )


def _validate_payload(payload: AddDiscoveredCollectedContentPayload) -> None:
    """
    Validates the AddDiscoveredCollectedContentPayload fields.
    Raises ValueError with a descriptive message on the first failing check.
    """
    if not payload.user_id or not payload.user_id.strip():
        raise ValueError("user_id must not be empty")

    if not payload.output_type or not payload.output_type.strip():
        raise ValueError("output_type must not be empty")

    if payload.content_type != "discovered_webpage":
        raise ValueError("content_type must be 'discovered_webpage'")

    if not payload.data or not payload.data.discovered_webpage:
        raise ValueError("data.discovered_webpage must not be empty")

    webpage_data = payload.data.discovered_webpage

    if not webpage_data.title or not webpage_data.title.strip():
        raise ValueError("data.discovered_webpage.title must not be empty")

    if not webpage_data.webpage_content or not webpage_data.webpage_content.strip():
        raise ValueError("data.discovered_webpage.webpage_content must not be empty")

    if not webpage_data.url or not webpage_data.url.strip():
        raise ValueError("data.discovered_webpage.url must not be empty")

    if not webpage_data.language or not webpage_data.language.strip():
        raise ValueError("data.discovered_webpage.language must not be empty")

    if webpage_data.category_name not in {c.value for c in CategoryName}:
        raise ValueError(
            f"Invalid data.discovered_webpage.category_name '{webpage_data.category_name}'. "
            f"Must be one of: {sorted(c.value for c in CategoryName)}"
        )

    if payload.created_at <= 0:
        raise ValueError("created_at must be a positive Unix timestamp")

    if payload.content_created_at <= 0:
        raise ValueError("content_created_at must be a positive Unix timestamp")
