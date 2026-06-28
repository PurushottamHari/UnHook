import logging

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from injector import inject

from ...external.user_service import UserServiceClient
from ...messaging.models.commands import (
    CreateNewspaperForUserCommand,
    CreateNewspaperForUserPayload,
)


@injectable()
class ProcessNewspaperForUserMessagingService:
    """Service to trigger newspaper creation by publishing a command."""

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
        Validates the user exists and publishes a CreateNewspaperForUserCommand.
        """
        self.logger.info(f"Triggering newspaper creation for user {user_id}")

        # Validate user exists before proceeding
        user = await self.user_service_client.get_user(user_id)
        if not user:
            self.logger.error(f"User {user_id} not found. Cannot process newspaper.")
            raise ValueError(f"User {user_id} not found.")

        # Construct and publish the command
        payload = CreateNewspaperForUserPayload(user_id=user_id)
        command = CreateNewspaperForUserCommand(payload=payload)

        await self.message_producer.send_command(command)
        self.logger.info(
            f"Successfully published CreateNewspaperForUserCommand for user {user_id}"
        )
