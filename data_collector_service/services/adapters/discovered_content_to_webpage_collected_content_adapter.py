from datetime import datetime, timezone

from commons.messaging.contracts.commands.data_collector_service.models import \
    AddDiscoveredCollectedContentPayload
from data_collector_service.models.webpage.webpage_collected_content import \
    WebpageCollectedContent


class DiscoveredContentToWebpageCollectedContentAdapter:
    """
    Adapts an AddDiscoveredCollectedContentPayload (received via the messaging
    contract) into a WebpageCollectedContent domain model, ready for storage and
    processing by the collection pipeline.
    """

    def convert_to_webpage_collected_content(
        self, payload: AddDiscoveredCollectedContentPayload
    ) -> WebpageCollectedContent:
        """
        Convert a discovered content payload into a WebpageCollectedContent instance.

        - Only maps data fields from the payload to the domain model.
        - Business logic fields (id, sha, status, created_at, version) are set elsewhere.

        Args:
            payload: Validated AddDiscoveredCollectedContentPayload.

        Returns:
            A WebpageCollectedContent domain model with data fields populated.
        """
        webpage_data = payload.data.discovered_webpage

        # Convert timestamps
        content_created_at = datetime.fromtimestamp(
            payload.content_created_at, tz=timezone.utc
        )

        return WebpageCollectedContent(
            id="",  # Will be set later not in adapter
            sha="",  # Will be set later not in adapter
            url=webpage_data.url,
            title=webpage_data.title,
            webpage_content=webpage_data.webpage_content,
            language=webpage_data.language,
            category_name=webpage_data.category_name,
            status=None,  # Will be set later not in adapter
            status_details=None,
            created_at=None,  # Will be set later not in adapter
            content_created_at=content_created_at,
            version=1,  # Will be set later not in adapter
        )
