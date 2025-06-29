"""
Service for generating required YouTube content for users.
"""

import asyncio
import logging
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
from data_processing_service.services.processing.youtube.ai_agent.content_generator import (
    ContentGenerator,
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
        self.content_generator_agent = ContentGenerator()
        self.logger = logging.getLogger(__name__)

    async def generate(self, user_id: str) -> None:
        """
        Generate required YouTube content for a specific user.
        Args:
            user_id: The user ID as a string
        """
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
        print(f"Found {len(content_to_generate_list)} items to generate content for")

        for content_to_generate in content_to_generate_list:
            try:
                # Use the AI Agent to generate the required content
                youtube_video_details = content_to_generate.data.get(
                    ContentType.YOUTUBE_VIDEO
                )
                subtitle_data = self.youtube_content_ephemeral_repository.get_all_clean_subtitle_file_data(
                    video_id=content_to_generate.external_id
                )
                selected_subtitle = self._select_best_subtitle(
                    subtitle_data, youtube_video_details
                )
                generated_data = (
                    await self.content_generator_agent.generate_required_content(
                        youtube_video_details=youtube_video_details,
                        subtitle_map=selected_subtitle,
                    )
                )

                # Create a generated content model using the required content, status: required_content_generated
                genrated_content_id = str(uuid.uuid4())
                generated_content = GeneratedContent(
                    id=genrated_content_id,
                    external_id=content_to_generate.external_id,  # Assuming this is the external id
                    content_type=ContentType.YOUTUBE_VIDEO,
                    generated={
                        OutputType.VERY_SHORT: generated_data[OutputType.VERY_SHORT],
                        OutputType.SHORT: generated_data[OutputType.SHORT],
                    },
                    status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
                    status_details=StatusDetail(
                        status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
                        created_at=datetime.utcnow(),
                        reason="Initial generation.",
                    ),
                    content_generated_at=youtube_video_details.release_date,
                )

                # Make the database write
                self.user_content_repository.add_generated_content(
                    generated_content=generated_content
                )

            except Exception as e:
                self.logger.error(
                    f"Content generation failed for {content_to_generate.external_id}: {e}"
                )
                continue

    def _select_best_subtitle(
        self, subtitle_data: SubtitleData, youtube_video_details: YouTubeVideoDetails
    ) -> SubtitleMap:
        """
        Select the best subtitle based on language and manual/automatic preference.
        Args:
            subtitle_data: SubtitleData object containing manual and automatic subtitles
            youtube_video_details: YouTubeVideoDetails object (should have a 'language' attribute)
        Returns:
            SubtitleMap: The selected subtitle map
        """
        preferred_language = youtube_video_details.language or "en"

        # 1. Prefer manual subtitle in preferred language
        for sub in subtitle_data.manual:
            if (
                sub.language.lower() == preferred_language.lower()
                and sub.subtitle.strip()
            ):
                return sub
        # 2. Prefer automatic subtitle in preferred language
        for sub in subtitle_data.automatic:
            if (
                sub.language.lower() == preferred_language.lower()
                and sub.subtitle.strip()
            ):
                return sub
        # 3. Any manual subtitle
        for sub in subtitle_data.manual:
            if sub.subtitle.strip():
                return sub
        # 4. Any automatic subtitle
        for sub in subtitle_data.automatic:
            if sub.subtitle.strip():
                return sub
        # 5. If nothing is available, raise an error or return a dummy SubtitleMap
        raise ValueError("No subtitles available to select.")


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
