"""
Service for generating required YouTube content for users.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime

from data_collector_service.collectors.youtube.models.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_collector_service.models import ContentType
from data_collector_service.models.user_collected_content import (
    ContentStatus,
    ContentSubStatus,
    ContentType,
)
from data_processing_service.external.user_service.client import UserServiceClient
from data_processing_service.models.generated_content import (
    GeneratedContent,
    GeneratedContentStatus,
    StatusDetail,
)
from data_processing_service.models.youtube.subtitle_data import (
    SubtitleData,
    SubtitleMap,
)
from data_processing_service.repositories.ephemeral.local.youtube_content_ephemeral_repository import (
    LocalYoutubeContentEphemeralRepository,
)
from data_processing_service.repositories.ephemeral.youtube_content_ephemeral_repository import (
    YoutubeContentEphemeralRepository,
)
from data_processing_service.repositories.mongodb.config.database import MongoDB
from data_processing_service.repositories.mongodb.user_content_repository import (
    MongoDBUserContentRepository,
)
from data_processing_service.repositories.user_content_repository import (
    UserContentRepository,
)
from data_processing_service.service_context import DataProcessingServiceContext
from data_processing_service.services.processing.youtube.generate_required_content.ai_agent.required_content_generator import (
    RequiredContentGenerator,
)
from data_processing_service.services.processing.youtube.generate_required_content.metrics_processor.generate_required_content_metrics_processor import (
    GenerateRequiredContentMetricsProcessor,
)
from data_processing_service.services.processing.youtube.process_moderated_content.subtitles.utils.subtitle_utils import (
    SubtitleUtils,
)
from user_service.models import OutputType
from user_service.models.user import User


class GenerateRequiredYoutubeContentService:
    """Service for generating required YouTube content for users."""

    def __init__(
        self,
        user_content_repository: UserContentRepository,
        youtube_content_ephemeral_repository: YoutubeContentEphemeralRepository,
    ):
        """
        Initialize the service with a user content repository.
        Args:
            user_content_repository: Repository for managing user content data
        """
        self.user_content_repository = user_content_repository
        self.user_service_client = UserServiceClient()
        self.youtube_content_ephemeral_repository = youtube_content_ephemeral_repository
        self.required_content_generator_agent = RequiredContentGenerator()
        self.subtitle_utils = SubtitleUtils()
        self.logger = logging.getLogger(__name__)

        # Initialize service context and metrics processor
        self.service_context = DataProcessingServiceContext(
            GenerateRequiredContentMetricsProcessor
        )
        self.metrics_processor = self.service_context.get_metrics_processor()

    async def generate(self, user_id: str) -> None:
        """
        Generate required YouTube content for a specific user.
        Args:
            user_id: The user ID as a string
        """
        try:
            # Fetch the user
            user = self.user_service_client.get_user(user_id)
            if not user:
                self.logger.error(f"User not found: {user_id}")
                return

            # Fetch all user collected content with status PROCESSING and sub_status SUBTITLES_STORED
            content_to_generate_list = self.user_content_repository.get_user_collected_content_without_generated_content(
                user_id=user.id,
                content_type=ContentType.YOUTUBE_VIDEO,
                status=ContentStatus.PROCESSING,
                sub_status=ContentSubStatus.SUBTITLES_STORED,
            )
            print(
                f"Found {len(content_to_generate_list)} items to generate content for"
            )

            # Record total content considered
            if self.metrics_processor:
                self.metrics_processor.record_content_considered(
                    len(content_to_generate_list)
                )

            for content_to_generate in content_to_generate_list:
                try:
                    # Use the AI Agent to generate the required content
                    youtube_video_details = content_to_generate.data.get(
                        ContentType.YOUTUBE_VIDEO
                    )
                    subtitle_data = self.youtube_content_ephemeral_repository.get_all_clean_subtitle_file_data(
                        video_id=content_to_generate.external_id
                    )

                    # Record subtitle download success
                    if self.metrics_processor:
                        subtitle_info = {
                            "video_id": content_to_generate.external_id,
                            "has_manual": bool(subtitle_data.manual),
                            "has_automatic": bool(subtitle_data.automatic),
                        }
                        self.metrics_processor.record_subtitle_download_success(
                            content_to_generate.external_id, subtitle_info
                        )

                    selected_subtitle = self.subtitle_utils.select_best_subtitle(
                        subtitle_data, youtube_video_details
                    )

                    # Record best subtitle download success
                    if self.metrics_processor:
                        self.metrics_processor.record_best_subtitle_download_success(
                            content_to_generate.external_id
                        )

                    generated_data = await self.required_content_generator_agent.generate_required_content(
                        youtube_video_details=youtube_video_details,
                        subtitle_map=selected_subtitle,
                    )

                    # Create a generated content model using the required content, status: required_content_generated
                    genrated_content_id = str(uuid.uuid4())
                    generated_content = GeneratedContent(
                        id=genrated_content_id,
                        external_id=content_to_generate.external_id,  # Assuming this is the external id
                        content_type=ContentType.YOUTUBE_VIDEO,
                        generated={
                            OutputType.VERY_SHORT: generated_data[
                                OutputType.VERY_SHORT
                            ],
                            OutputType.SHORT: generated_data[OutputType.SHORT],
                        },
                        status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
                        status_details=[
                            StatusDetail(
                                status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
                                created_at=datetime.utcnow(),
                                reason="Initial generation.",
                            )
                        ],
                        content_generated_at=youtube_video_details.release_date,
                    )

                    # Make the database write
                    self.user_content_repository.add_generated_content(
                        generated_content=generated_content
                    )
                    print(
                        f"Operation completed successfully for external_id: {content_to_generate.external_id}"
                    )

                except Exception as e:
                    # Record complete failure
                    if self.metrics_processor:
                        self.metrics_processor.record_complete_failure(
                            content_to_generate.external_id, str(e)
                        )
                    self.logger.error(
                        f"Content generation failed for {content_to_generate.external_id}: {str(e)}"
                    )
                    continue

            # Complete metrics collection
            if self.metrics_processor:
                self.metrics_processor.complete(success=True)
                print(
                    f"✅ Generate required content completed. Considered: {self.metrics_processor.get_total_considered()}, "
                    f"Subtitle downloads: {self.metrics_processor.get_subtitle_download_success_count()}, "
                    f"Best subtitle downloads: {self.metrics_processor.get_best_subtitle_download_success_count()}, "
                    f"Failures: {self.metrics_processor.get_complete_failures_count()}"
                )

        except Exception as e:
            # Complete metrics collection with error
            if self.metrics_processor:
                self.metrics_processor.complete(success=False, error_message=str(e))
            raise


if __name__ == "__main__":
    # Example usage for testing
    USER_ID = "607d95f0-47ef-444c-89d2-d05f257d1265"  # Replace with actual user id
    # Initialize repositories (replace with actual implementations as needed)
    MongoDB.connect_to_database()
    database = MongoDB.get_database()
    user_content_repository = MongoDBUserContentRepository(database)
    youtube_content_ephemeral_repository = LocalYoutubeContentEphemeralRepository()
    service = GenerateRequiredYoutubeContentService(
        user_content_repository, youtube_content_ephemeral_repository
    )
    asyncio.run(service.generate(USER_ID))
