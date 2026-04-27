import logging
from copy import deepcopy

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.events.data_processing_service.models import (
    GeneratedYoutubeContentArticleReadyEvent,
    GeneratedYoutubeContentArticleReadyPayload)
from data_collector_service.models.enums import ContentType
from data_processing_service.config import Config
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)
from data_processing_service.repositories.ephemeral.youtube_content_ephemeral_repository import \
    YoutubeContentEphemeralRepository
from data_processing_service.repositories.user_content_repository import \
    UserContentRepository
from data_processing_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository
from data_processing_service.services.processing.youtube.generate_complete_content.ai_agent.complete_content_generator import \
    CompleteContentGenerator
from data_processing_service.services.processing.youtube.utils.subtitle_utils import \
    SubtitleUtils
from data_processing_service.utils.content_utils import calculate_reading_time
from user_service.models import OutputType


@injectable()
class GenerateCompleteContentForYoutubeService:
    """Service for generating complete YouTube content for a single content item."""

    @inject
    def __init__(
        self,
        user_content_repository: UserContentRepository,
        youtube_content_ephemeral_repository: YoutubeContentEphemeralRepository,
        subtitle_utils: SubtitleUtils,
        complete_content_generator: CompleteContentGenerator,
        youtube_collected_content_repository: YouTubeCollectedContentRepository,
        message_producer: MessageProducer,
    ):
        self.user_content_repository = user_content_repository
        self.youtube_content_ephemeral_repository = youtube_content_ephemeral_repository
        self.subtitle_utils = subtitle_utils
        self.complete_content_generator = complete_content_generator
        self.youtube_collected_content_repository = youtube_collected_content_repository
        self.message_producer = message_producer
        self.logger = logging.getLogger(__name__)

    async def generate_for_content(self, generated_content_id: str) -> None:
        """
        Processes a single generated content ID.
        """
        # Fetch generated content
        generated_content_list = (
            self.user_content_repository.get_generated_content_by_ids(
                [generated_content_id]
            )
        )
        if not generated_content_list:
            self.logger.error(
                f"Generated content with ID {generated_content_id} not found."
            )
            raise ValueError(
                f"Generated content with ID {generated_content_id} not found."
            )

        content = generated_content_list[0]

        if content.content_type != ContentType.YOUTUBE_VIDEO:
            self.logger.error(
                f"Generated content with ID {generated_content_id} is not a YouTube video."
            )
            raise ValueError(
                f"Generated content with ID {generated_content_id} is not a YouTube video."
            )

        if content.status == GeneratedContentStatus.CATEGORIZATION_COMPLETED:
            self.logger.info(f"🚀 Processing generation for {generated_content_id}")

            # Fetch YouTube video details directly from the repository
            youtube_video_details = (
                self.youtube_collected_content_repository.get_video_by_id(
                    content.external_id
                )
            )
            if not youtube_video_details:
                self.logger.error(
                    f"YouTube video details for external ID {content.external_id} not found."
                )
                raise ValueError(
                    f"YouTube video details for external ID {content.external_id} not found."
                )

            subtitle_data = self.youtube_content_ephemeral_repository.get_all_clean_subtitle_file_data(
                video_id=content.external_id
            )

            if not subtitle_data.manual and not subtitle_data.automatic:
                self.logger.warning(
                    f"No clean subtitles found for video_id {content.external_id}, skipping."
                )
                raise ValueError(
                    f"No clean subtitles found for video_id {content.external_id}"
                )

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

            # Create a deep copy for the generated content with the updated details
            generated_content_clone = deepcopy(updated_content)

            # Update status
            generated_content_clone.set_status(
                GeneratedContentStatus.ARTICLE_GENERATED,
                "Article Generation Complete.",
            )
            generated_content_clone.version += 1
            # Calculate reading time
            generated_content_clone.reading_time_seconds = self._calculate_reading_time(
                generated_content_clone
            )

            # Make an update generated content repo call
            self.user_content_repository.update_generated_content(
                generated_content_clone
            )
            self.logger.info(
                f"✅ Article generated and updated for ID {generated_content_id}"
            )

        elif content.status == GeneratedContentStatus.ARTICLE_GENERATED:
            self.logger.info(
                f"Article already generated for {generated_content_id}, skipping processing part."
            )
        else:
            self.logger.error(
                f"❌ Invalid status {content.status} for {generated_content_id}. Expected CATEGORIZATION_COMPLETED or ARTICLE_GENERATED."
            )
            raise ValueError(
                f"Invalid status {content.status} for {generated_content_id}"
            )

        # At the end, publish an event signifying that the article has been generated
        # Fetch user_id from UserCollectedContent to include in the event
        user_collected_content_list = (
            self.user_content_repository.get_user_collected_content_by_external_ids(
                [content.external_id]
            )
        )
        if not user_collected_content_list:
            self.logger.error(
                f"User collected content for external ID {content.external_id} not found."
            )
            raise ValueError(
                f"User collected content for external ID {content.external_id} not found."
            )
        user_id = user_collected_content_list[0].user_id

        # Draft and publish the event
        generation_complete_event = GeneratedYoutubeContentArticleReadyEvent(
            payload=GeneratedYoutubeContentArticleReadyPayload(
                user_id=user_id,
                generated_content_id=generated_content_id,
                external_id=content.external_id,
            )
        )

        await self.message_producer.publish_event(generation_complete_event)
        self.logger.info(
            f"📤 Published GeneratedYoutubeContentArticleReadyEvent for {generated_content_id}"
        )

    def _calculate_reading_time(self, generated_content: GeneratedContent) -> int:
        """
        Calculate the reading time for the generated content.
        """
        generated = generated_content.generated
        article_content = ""
        if OutputType.MEDIUM in generated:
            article_content = generated[OutputType.MEDIUM].string
        elif OutputType.LONG in generated:
            article_content = generated[OutputType.LONG].string

        if not article_content:
            raise ValueError(
                f"No article content found in generated content (id: {generated_content.id})."
            )

        return calculate_reading_time(article_content)
