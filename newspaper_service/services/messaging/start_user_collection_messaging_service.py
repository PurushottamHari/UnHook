import logging

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.commands.data_collector_service.models import (
    StartUserCollectionCommand,
    StartUserCollectionPayload,
)
from injector import inject

from ...external.user_service import UserServiceClient


@injectable()
class StartUserCollectionMessagingService:
    """Service to trigger user collection by publishing a command."""

    @inject
    def __init__(
        self,
        message_producer: MessageProducer,
        user_service_client: UserServiceClient,
    ):
        self.message_producer = message_producer
        self.user_service_client = user_service_client
        self.logger = logging.getLogger(__name__)

    async def execute(self, user_id: str) -> None:
        """
        Validates the user exists and publishes a StartUserCollectionCommand.
        """
        self.logger.info(f"Triggering user collection for user {user_id}")

        # Validate user exists before proceeding
        user = await self.user_service_client.get_user(user_id)
        if not user:
            self.logger.error(f"User {user_id} not found. Cannot start collection.")
            raise ValueError(f"User {user_id} not found.")

        # Construct and publish the command
        payload = StartUserCollectionPayload(user_id=user_id)
        command = StartUserCollectionCommand(payload=payload)

        await self.message_producer.send_command(command)
        self.logger.info(
            f"Successfully published StartUserCollectionCommand for user {user_id}"
        )
