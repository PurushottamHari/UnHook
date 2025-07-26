import asyncio
import logging
from copy import deepcopy

from services.processing.youtube.generate_complete_content.ai_agent.complete_content_generator import \
    CompleteContentGenerator

from data_collector_service.models.enums import ContentType
from data_collector_service.models.user_collected_content import ContentStatus
from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from data_processing_service.repositories.ephemeral.local.youtube_content_ephemeral_repository import \
    LocalYoutubeContentEphemeralRepository
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.user_content_repository import \
    MongoDBUserContentRepository
from data_processing_service.services.processing.youtube.process_moderated_content.subtitles.utils.subtitle_utils import \
    SubtitleUtils


class GenerateCompleteYoutubeContentService:
    """Service for generating complete YouTube content for users."""

    def __init__(self):
        # Initialize MongoDB connection if not already connected
        if MongoDB.db is None:
            MongoDB.connect_to_database()
        # Create MongoDB user content repository
        self.user_content_repository = MongoDBUserContentRepository(
            MongoDB.get_database()
        )
        self.youtube_content_ephemeral_repository = (
            LocalYoutubeContentEphemeralRepository()
        )
        self.subtitle_utils = SubtitleUtils()
        self.complete_content_generator = CompleteContentGenerator()
        self.logger = logging.getLogger(__name__)

    async def generate_complete_content(self) -> None:
        """
        Fetch all generated content with status CATEGORIZATION_COMPLETED and process them.
        The processing logic for each entry is to be implemented.
        """
        generated_content_list = self.user_content_repository.get_generated_content(
            status=GeneratedContentStatus.CATEGORIZATION_COMPLETED,
            content_type=ContentType.YOUTUBE_VIDEO,
        )
        print(
            f"Found {len(generated_content_list)} generated content items with status CATEGORIZATION_COMPLETED"
        )

        # Collect all external_ids
        external_ids = [content.external_id for content in generated_content_list]
        # Fetch all UserCollectedContent objects in one DB call
        user_collected_content_list = (
            self.user_content_repository.get_user_collected_content_by_external_ids(
                external_ids
            )
        )
        # Map for quick lookup
        user_collected_content_map = {
            content.external_id: content for content in user_collected_content_list
        }

        for content in generated_content_list:
            external_id = content.external_id
            user_collected_content = user_collected_content_map.get(external_id)
            youtube_video_details = user_collected_content.data.get(
                ContentType.YOUTUBE_VIDEO
            )
            subtitle_data = self.youtube_content_ephemeral_repository.get_all_clean_subtitle_file_data(
                video_id=external_id
            )
            # Skip if no clean subtitles are found
            if not subtitle_data.manual and not subtitle_data.automatic:
                print(f"No clean subtitles found for video_id {external_id}, skipping.")
                continue

            selected_subtitle = self.subtitle_utils.select_best_subtitle(
                subtitle_data, youtube_video_details
            )
            updated_content = (
                await self.complete_content_generator.generate_for_generated_content(
                    content=content,
                    content_data=selected_subtitle.subtitle,
                    content_language=selected_subtitle.language,
                )
            )
            generated_content_clone = deepcopy(updated_content)
            # Update timestamp and status
            generated_content_clone.set_status(
                GeneratedContentStatus.ARTICLE_GENERATED,
                "Article Generation Complete.",
            )
            user_collected_content_clone = deepcopy(user_collected_content)
            user_collected_content_clone.set_status(
                ContentStatus.PROCESSED,
                "User Collected Content Processed.",
            )
            self.user_content_repository.update_user_collected_content_and_generated_content(
                user_collected_content=user_collected_content_clone,
                generated_content=generated_content_clone,
            )
            print(f"Article generated for id {generated_content_clone.id}")
        print("Service Complete....")


if __name__ == "__main__":
    service = GenerateCompleteYoutubeContentService()
    asyncio.run(service.generate_complete_content())
