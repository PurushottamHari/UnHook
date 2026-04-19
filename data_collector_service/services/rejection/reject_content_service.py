"""
Service for handling content rejection.
"""

import asyncio
from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.models.enums import ContentType
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository

from .service_context import RejectionServiceContext
from .youtube.ai_agent.moderator import ContentModerator
from .youtube.rejection_content_service_youtube import \
    RejectionContentServiceYoutube


@injectable()
class RejectContentService:
    """Service for handling content rejection."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        user_content_repository: UserCollectedContentRepository,
        service_context: RejectionServiceContext,
        rejection_content_service_youtube: RejectionContentServiceYoutube,
    ):
        """
        Initialize the service.

        Args:
            user_service_client: Client for user service
            user_content_repository: Repository for user collected content
            service_context: Service context for rejection
            rejection_content_service_youtube: YouTube-specific rejection service
        """
        self.user_service_client = user_service_client
        self.user_content_repository = user_content_repository
        self.service_context = service_context
        self.rejection_content_service_youtube = rejection_content_service_youtube

        # Get the auto-initialized metrics processor
        self.metrics_processor = self.service_context.get_rejection_metrics_processor()

    async def reject(self, user_id: str) -> None:
        """
        Reject content for a user.

        Args:
            user_id: The ID of the user
        """
        try:
            # Get user object from user service
            user = await self.user_service_client.get_user(user_id)

            # Get unprocessed content for the user
            unprocessed_content_list = (
                self.user_content_repository.get_unprocessed_content_for_user(user_id)
            )

            # Record total content considered
            if self.metrics_processor:
                self.metrics_processor.record_content_considered(
                    len(unprocessed_content_list)
                )

            # Collect unprocessed content in a map by content_type
            content_map = {}
            for unprocessed_content in unprocessed_content_list:
                content_type = unprocessed_content.content_type
                if content_type not in content_map:
                    content_map[content_type] = []
                content_map[content_type].append(unprocessed_content)

            # Process each content type
            rejected_content = []
            for content_type, contents in content_map.items():
                if content_type == ContentType.YOUTUBE_VIDEO:
                    print(f"Found {len(contents)} elements to process for Youtube")

                    # Record channel processing
                    if self.metrics_processor:
                        # Extract channel from first content item (assuming same channel for batch)
                        if contents:
                            channel_name = getattr(
                                contents[0], "channel_name", "unknown"
                            )
                            self.metrics_processor.record_channel_processed(
                                channel_name
                            )

                    moderated_youtube_content = (
                        await self.rejection_content_service_youtube.reject(
                            user=user, contents=contents
                        )
                    )
                    if len(moderated_youtube_content) != len(contents):
                        raise ValueError(
                            f"Mismatch in moderated content count: expected {len(contents)}, got {len(moderated_youtube_content)}"
                        )
                    rejected_content.extend(moderated_youtube_content)
                else:
                    for content in contents:
                        print(
                            "Unsupported Content type!: "
                            + content.id
                            + " - "
                            + content_type
                        )

            if len(rejected_content) != 0:
                self.user_content_repository.upsert_user_collected_content_batch(
                    rejected_content
                )

            # Complete metrics collection
            if self.metrics_processor:
                self.metrics_processor.calculate_success_rate()
                self.metrics_processor.complete(success=True)
                print(
                    f"✅ Rejection completed. Considered: {self.metrics_processor.get_total_considered()}, Rejected: {self.metrics_processor.get_total_rejected()}"
                )

        except Exception as e:
            # Complete metrics collection with error
            if self.metrics_processor:
                self.metrics_processor.complete(success=False, error_message=str(e))
            raise


if __name__ == "__main__":
    print("🚀 Starting Rejection Service...")

    user_service_client = UserServiceClient()
    reject_content_service = RejectContentService(user_service_client)

    # Call reject with a custom user_id
    custom_user_id = (
        "607d95f0-47ef-444c-89d2-d05f257d1265"  # Replace with your desired user_id
    )
    asyncio.run(reject_content_service.reject(custom_user_id))
