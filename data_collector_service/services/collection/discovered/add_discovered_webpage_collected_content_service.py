import hashlib
import logging
import re
import uuid
from datetime import datetime, timezone

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.commands.data_processing_service.models import (
    StartDataProcessingForUserCollectedContentCommand,
    StartDataProcessingForUserCollectedContentPayload)
from data_collector_service.models.enums import ContentType
from data_collector_service.models.user_collected_content import (
    ContentStatus, StatusDetail, UserCollectedContent)
from data_collector_service.models.webpage.webpage_collected_content import (
    WebpageCollectedContent, WebpageStatus)
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from data_collector_service.repositories.webpage_collected_content_repository import \
    WebpageCollectedContentRepository

logger = logging.getLogger(__name__)


@injectable()
class AddDiscoveredWebpageCollectedContentService:
    """Handles storage/processing of a discovered webpage collected content entry."""

    @inject
    def __init__(
        self,
        webpage_repository: WebpageCollectedContentRepository,
        user_collected_content_repository: UserCollectedContentRepository,
        message_producer: MessageProducer,
    ):
        """
        Initialize the service.

        Args:
            webpage_repository: Repository for webpage content storage and retrieval.
            user_collected_content_repository: Repository for user collected content storage and retrieval.
            message_producer: Message producer for publishing commands to the message queue.
        """
        self.webpage_repository = webpage_repository
        self.user_collected_content_repository = user_collected_content_repository
        self.message_producer = message_producer

    async def add_discovered_webpage_content(
        self, webpage: WebpageCollectedContent, user_id: str, output_type: str
    ) -> None:
        """
        Process and persist a discovered webpage collected content.

        Steps:
        1. Set business logic fields (id, sha, status, created_at, version).
        2. Validate the webpage content data.
        3. Check if content already exists by SHA hash.
        4. If exists, skip storage and proceed to message.
        5. If not exists, persist to repository.
        6. Create UserCollectedContent entry and upsert for the user.
        7. Add message to Redis (placeholder for future implementation).

        Args:
            webpage: The WebpageCollectedContent model with data fields populated.
            user_id: The ID of the user who collected this content.
            output_type: The output type for the collected content.

        Raises:
            ValueError: If validation fails.
        """
        now_timestamp = datetime.now(tz=timezone.utc)
        webpage.sha = hashlib.sha256(
            webpage.webpage_content.encode("utf-8")
        ).hexdigest()

        # Validate the webpage content
        self._validate_webpage_content(webpage)

        webpage_content = None

        # Check if content already exists by SHA
        webpage_content = self.webpage_repository.get_webpage_by_sha(webpage.sha)
        if webpage_content:
            logger.info(
                f"[AddDiscoveredWebpageCollectedContentService] Webpage with SHA {webpage.sha} "
                f"already exists, skipping storage"
            )
        else:
            logger.info(
                f"[AddDiscoveredWebpageCollectedContentService] New webpage with SHA {webpage.sha}, "
                f"persisting to repository"
            )
            webpage.id = str(uuid.uuid4())
            webpage.status = WebpageStatus.COLLECTED
            webpage.created_at = now_timestamp
            webpage.updated_at = now_timestamp
            webpage.version = 1
            self.webpage_repository.upsert_webpages([webpage])
            webpage_content = webpage

        # Create UserCollectedContent entry and upsert for the user
        print("DEBUG: Creating UserCollectedContent entry")
        user_collected_content = UserCollectedContent(
            id=str(uuid.uuid4()),
            content_type=ContentType.DISCOVERED_WEBPAGE,
            user_id=user_id,
            external_id=webpage.id,
            output_type=output_type,
            status=ContentStatus.COLLECTED,
            status_details=[
                StatusDetail(
                    status=ContentStatus.COLLECTED,
                    created_at=datetime.now(tz=timezone.utc),
                    reason="Webpage content collected",
                )
            ],
            data={},
            version=1,
            created_at=now_timestamp,
            updated_at=now_timestamp,
            content_created_at=webpage_content.content_created_at,
        )
        # In this flow, no moderation is needed and hence we can mark it as PROCESSED as well
        user_collected_content.set_status(ContentStatus.PROCESSED)
        self.user_collected_content_repository.upsert_user_collected_content_batch(
            [user_collected_content]
        )
        logger.info(
            f"[AddDiscoveredWebpageCollectedContentService] UserCollectedContent entry created "
            f"for user {user_id} with external_id {webpage.id}"
        )

        # 7. Publish command to Start Data Processing Service
        payload = StartDataProcessingForUserCollectedContentPayload(
            user_id=user_id,
            user_collected_content_id=user_collected_content.id,
        )
        command = StartDataProcessingForUserCollectedContentCommand(payload=payload)

        await self.message_producer.send_command(command=command)

        logger.info(
            f"[AddDiscoveredWebpageCollectedContentService] Published command to start data processing "
            f"for user_collected_content_id {user_collected_content.id}"
        )

    def _validate_webpage_content(self, webpage: WebpageCollectedContent) -> None:
        """
        Validate that all required fields are present and in the correct format.

        Args:
            webpage: The WebpageCollectedContent to validate.

        Raises:
            ValueError: If any required field is missing or invalid.
        """

        if not webpage.sha or not webpage.sha.strip():
            raise ValueError("Webpage SHA must not be empty")

        if not webpage.url or not webpage.url.strip():
            raise ValueError("Webpage URL must not be empty")

        # Validate URL format
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if not url_pattern.match(webpage.url):
            raise ValueError(f"Webpage URL '{webpage.url}' is not a valid URL")

        if not webpage.title or not webpage.title.strip():
            raise ValueError("Webpage title must not be empty")

        if not webpage.webpage_content or not webpage.webpage_content.strip():
            raise ValueError("Webpage content must not be empty")

        if not webpage.language or not webpage.language.strip():
            raise ValueError("Webpage language must not be empty")

        if not webpage.category_name or not webpage.category_name.strip():
            raise ValueError("Webpage category_name must not be empty")
