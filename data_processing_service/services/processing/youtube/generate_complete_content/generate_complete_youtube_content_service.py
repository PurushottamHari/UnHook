import asyncio
import logging
import time
from copy import deepcopy

from data_collector_service.models.enums import ContentType
from data_collector_service.models.user_collected_content import ContentStatus
from data_processing_service.models.generated_content import (
    GeneratedContent,
    GeneratedContentStatus,
)
from data_processing_service.repositories.ephemeral.local.youtube_content_ephemeral_repository import (
    LocalYoutubeContentEphemeralRepository,
)
from data_processing_service.repositories.mongodb.config.database import MongoDB
from data_processing_service.repositories.mongodb.user_content_repository import (
    MongoDBUserContentRepository,
)
from data_processing_service.service_context import DataProcessingServiceContext
from data_processing_service.services.processing.youtube.generate_complete_content.ai_agent.complete_content_generator import (
    CompleteContentGenerator,
)
from data_processing_service.services.processing.youtube.generate_complete_content.metrics_processor.generate_complete_content_metrics_processor import (
    GenerateCompleteContentMetricsProcessor,
)
from data_processing_service.services.processing.youtube.process_moderated_content.subtitles.utils.subtitle_utils import (
    SubtitleUtils,
)
from data_processing_service.utils.content_utils import calculate_reading_time
from user_service.models import OutputType


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

        # Initialize service context and metrics processor
        self.service_context = DataProcessingServiceContext(
            GenerateCompleteContentMetricsProcessor
        )
        self.metrics_processor = self.service_context.get_metrics_processor()

    async def generate_complete_content(self) -> None:
        """
        Fetch all generated content with status CATEGORIZATION_COMPLETED and process them.
        The processing logic for each entry is to be implemented.
        """
        try:
            generated_content_list = self.user_content_repository.get_generated_content(
                status=GeneratedContentStatus.CATEGORIZATION_COMPLETED,
                content_type=ContentType.YOUTUBE_VIDEO,
            )
            print(
                f"Found {len(generated_content_list)} generated content items with status CATEGORIZATION_COMPLETED"
            )

            # Record total content considered
            if self.metrics_processor:
                self.metrics_processor.record_content_considered(
                    len(generated_content_list)
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
                try:
                    start_time = time.time()
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
                        print(
                            f"No clean subtitles found for video_id {external_id}, skipping."
                        )
                        continue

                    selected_subtitle = self.subtitle_utils.select_best_subtitle(
                        subtitle_data, youtube_video_details
                    )
                    updated_content = await self.complete_content_generator.generate_for_generated_content(
                        content=content,
                        content_data=selected_subtitle.subtitle,
                        content_language=selected_subtitle.language,
                    )
                    generation_time = time.time() - start_time

                    # Record successful generation
                    if self.metrics_processor:
                        self.metrics_processor.record_successful_generation(
                            content.id, generation_time
                        )

                    generated_content_clone = deepcopy(updated_content)
                    # Update timestamp and status
                    generated_content_clone.set_status(
                        GeneratedContentStatus.ARTICLE_GENERATED,
                        "Article Generation Complete.",
                    )
                    generated_content_clone.reading_time_seconds = (
                        self._calculate_reading_time(generated_content_clone)
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

                except Exception as e:
                    # Record generation failure
                    if self.metrics_processor:
                        self.metrics_processor.record_generation_failure(
                            content.id, str(e)
                        )
                    self.logger.error(
                        f"Content generation failed for {content.external_id}: {str(e)}"
                    )
                    continue

            # Complete metrics collection
            if self.metrics_processor:
                self.metrics_processor.complete(success=True)
                print(
                    f"✅ Generate complete content completed. Considered: {self.metrics_processor.get_total_considered()}, "
                    f"Successfully generated: {self.metrics_processor.get_successfully_generated_count()}, "
                    f"Failures: {self.metrics_processor.get_generation_failures_count()}, "
                    f"Average generation time: {self.metrics_processor.get_average_generation_time():.2f}s"
                )

        except Exception as e:
            # Complete metrics collection with error
            if self.metrics_processor:
                self.metrics_processor.complete(success=False, error_message=str(e))
            raise

        print("Service Complete....")

    def _calculate_reading_time(self, generated_content: GeneratedContent) -> int:
        """
        Calculate the reading time for the generated content.

        Args:
            generated_content: The generated content object containing MEDIUM or LONG articles

        Returns:
            int: Reading time in seconds

        Raises:
            ValueError: If neither MEDIUM nor LONG article content is found
        """
        generated = generated_content.generated

        # Try to get article content from MEDIUM or LONG output types
        article_content = ""
        if OutputType.MEDIUM in generated:
            article_content = generated[OutputType.MEDIUM].string
        elif OutputType.LONG in generated:
            article_content = generated[OutputType.LONG].string

        if not article_content:
            raise ValueError(
                f"No article content found in generated content (id: {generated_content.id}). "
                f"Expected either MEDIUM or LONG output type, but found: {list(generated.keys())}"
            )

        return calculate_reading_time(article_content)


if __name__ == "__main__":
    service = GenerateCompleteYoutubeContentService()
    asyncio.run(service.generate_complete_content())
