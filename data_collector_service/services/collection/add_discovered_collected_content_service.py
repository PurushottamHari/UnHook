import logging

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging.contracts.commands.data_collector_service.models import \
    AddDiscoveredCollectedContentPayload
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.models.enums import ContentType
from data_collector_service.models.webpage.webpage_collected_content import \
    WebpageCollectedContent
from data_collector_service.services.adapters.discovered_content_to_webpage_collected_content_adapter import \
    DiscoveredContentToWebpageCollectedContentAdapter
from data_collector_service.services.collection.discovered.add_discovered_webpage_collected_content_service import \
    AddDiscoveredWebpageCollectedContentService

logger = logging.getLogger(__name__)


@injectable()
class AddDiscoveredCollectedContentService:
    """Orchestrates the ingestion of externally discovered content by validating the user
    and delegating to the appropriate content-type handler."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        add_discovered_webpage_collected_content_service: AddDiscoveredWebpageCollectedContentService,
        adapter: DiscoveredContentToWebpageCollectedContentAdapter,
    ):
        """
        Initialize the service.

        Args:
            user_service_client: Client used to validate that the user exists.
            add_discovered_webpage_collected_content_service: Handler for DISCOVERED_WEBPAGE content.
            adapter: Converts the incoming payload into a WebpageCollectedContent domain model.
        """
        self.user_service_client = user_service_client
        self.add_discovered_webpage_collected_content_service = (
            add_discovered_webpage_collected_content_service
        )
        self.adapter = adapter

    async def add_discovered_content(
        self, payload: AddDiscoveredCollectedContentPayload
    ) -> None:
        """
        Validate the user, adapt the payload into a WebpageCollectedContent model,
        and dispatch to the correct content-type handler.

        Args:
            payload: Validated AddDiscoveredCollectedContentPayload from the command.

        Raises:
            ValueError: If the user cannot be found.
            TypeError: If the content_type in the adapted model is not supported.
        """
        # 1. Validate user
        user = await self.user_service_client.get_user(payload.user_id)
        if not user:
            logger.error(f"User {payload.user_id} not found.")
            raise ValueError(f"User with id '{payload.user_id}' not found.")
        # 3. Dispatch based on content_type
        match payload.content_type:
            case "discovered_webpage":
                logger.info(
                    f"[AddDiscoveredCollectedContentService] Routing DISCOVERED_WEBPAGE "
                    f"content for user {payload.user_id}"
                )
                # 2. Adapt the typed payload into the domain model
                webpage_collected_content = (
                    self.adapter.convert_to_webpage_collected_content(payload)
                )

                await self.add_discovered_webpage_collected_content_service.add_discovered_webpage_content(
                    webpage=webpage_collected_content,
                    user_id=payload.user_id,
                    output_type=payload.output_type,
                )

            case _:
                raise TypeError(
                    f"Content type '{payload.content_type}' is not supported."
                )
