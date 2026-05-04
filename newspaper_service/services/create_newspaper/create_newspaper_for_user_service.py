import logging
from datetime import datetime, timezone
from uuid import uuid4

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer

from ...external.user_service import UserServiceClient
from ...messaging.models.commands import (StartCollationForNewspaperCommand,
                                          StartCollationForNewspaperPayload)
from ...models import NewspaperStatus, NewspaperV2
from ...repositories import NewspaperV2Repository


@injectable()
class CreateNewspaperForUserService:
    """Service to create a newspaper and start the collation process."""

    @inject
    def __init__(
        self,
        newspaper_repository: NewspaperV2Repository,
        message_producer: MessageProducer,
        user_service_client: UserServiceClient,
    ):
        self.newspaper_repository = newspaper_repository
        self.message_producer = message_producer
        self.user_service_client = user_service_client
        self.logger = logging.getLogger(__name__)

    async def execute(self, user_id: str) -> NewspaperV2:
        """
        Creates a newspaper for a user if it doesn't exist for today,
        and starts the collation process.
        """
        self.logger.info(
            f"Checking for existing newspaper for user {user_id} for today"
        )

        # Validate user exists before proceeding
        user = await self.user_service_client.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found. Cannot create newspaper.")

        # Determine "today" (UTC 00:00:00)
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Check if newspaper exists for today
        newspaper = self.newspaper_repository.get_by_user_and_date(user_id, today)

        if not newspaper:
            self.logger.info(
                f"No newspaper found for user {user_id} for {today}. Creating new one."
            )
            # Create new NewspaperV2 if it doesn't exist
            newspaper = NewspaperV2(
                id=str(uuid4()),
                user_id=user_id,
                created_at=today,
                status=NewspaperStatus.COLLATING,
                version=1,  # Explicit versioning for optimistic locking
            )
            newspaper.set_status(
                NewspaperStatus.COLLATING, "Starting newspaper collation"
            )

            # Save to repository
            self.newspaper_repository.upsert(newspaper)
        else:
            self.logger.info(
                f"Found existing newspaper {newspaper.id} for user {user_id} for {today}."
            )

        # Publish command (ALWAYS sent regardless of whether it was just created or already existed)
        self.logger.info(
            f"Publishing StartCollationForNewspaperCommand for newspaper {newspaper.id}"
        )
        payload = StartCollationForNewspaperPayload(
            newspaper_id=newspaper.id, user_id=user_id
        )
        command = StartCollationForNewspaperCommand(payload=payload)
        await self.message_producer.send_command(command)

        return newspaper
