"""
Service for generating required YouTube content for a single item.
"""

import logging
import uuid
from datetime import datetime

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging.aggregated_schedule import AggregatedScheduleService
from data_collector_service.models.user_collected_content import (
    ContentSubStatus, ContentType, UserCollectedContent)
from data_processing_service.config.config import Config
from data_processing_service.messaging.models.commands import (
    CategorizeGeneratedYoutubeContentAggregationCommand,
    CategorizeGeneratedYoutubeContentAggregationPayload)
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus, StatusDetail)
from data_processing_service.repositories.ephemeral.youtube_content_ephemeral_repository import \
    YoutubeContentEphemeralRepository
from data_processing_service.repositories.generated_content_repository import \
    GeneratedContentRepository
from data_processing_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository
from data_processing_service.services.processing.youtube.generate_required_content.ai_agent.required_content_generator import \
    RequiredContentGenerator
from data_processing_service.services.processing.youtube.utils.subtitle_utils import \
    SubtitleUtils
from user_service.models import OutputType


@injectable()
class GenerateRequiredContentForYoutubeService:
    """Service for generating required YouTube content for a single user collected content item."""

    @inject
    def __init__(
        self,
        generated_content_repository: GeneratedContentRepository,
        youtube_collected_content_repository: YouTubeCollectedContentRepository,
        youtube_content_ephemeral_repository: YoutubeContentEphemeralRepository,
        required_content_generator_agent: RequiredContentGenerator,
        subtitle_utils: SubtitleUtils,
        aggregated_schedule_service: AggregatedScheduleService,
    ):
        """
        Initialize the service with dependencies.
        Args:
            generated_content_repository: Repository for managing generated content data
            youtube_collected_content_repository: Repository for raw YouTube video details
            youtube_content_ephemeral_repository: Repository for ephemeral subtitle storage
            required_content_generator_agent: AI agent for content generation
            subtitle_utils: Utility for subtitle selection (local implementation)
        """
        self.generated_content_repository = generated_content_repository
        self.youtube_collected_content_repository = youtube_collected_content_repository
        self.youtube_content_ephemeral_repository = youtube_content_ephemeral_repository
        self.required_content_generator_agent = required_content_generator_agent
        self.subtitle_utils = subtitle_utils
        self.aggregated_schedule_service = aggregated_schedule_service
        self.logger = logging.getLogger(__name__)

    async def generate_required_content(
        self, user_collected_content: UserCollectedContent
    ) -> str:
        """
        Generate required YouTube content for a specific user collected content item.
        Args:
            user_collected_content: The UserCollectedContent object
        Returns:
            str: The ID of the newly created GeneratedContent item
        """
        if user_collected_content.content_type != ContentType.YOUTUBE_VIDEO:
            raise ValueError(
                f"Unsupported content type: {user_collected_content.content_type}"
            )

        if user_collected_content.sub_status != ContentSubStatus.SUBTITLES_STORED:
            raise ValueError(
                f"Content {user_collected_content.id} is not in SUBTITLES_STORED status. "
                f"Current sub_status: {user_collected_content.sub_status}"
            )

        # Verify no generated content exists yet for this external_id
        existing_generated_content = (
            self.generated_content_repository.get_generated_content_by_external_id(
                external_id=user_collected_content.external_id,
                content_type=ContentType.YOUTUBE_VIDEO,
            )
        )
        if existing_generated_content:
            raise ValueError(
                f"Generated content already exists for external_id: {user_collected_content.external_id}"
            )

        # Fetch YouTube details
        youtube_video_details = (
            self.youtube_collected_content_repository.get_video_by_id(
                video_id=user_collected_content.external_id
            )
        )
        if not youtube_video_details:
            raise ValueError(
                f"YouTube details not found for video_id: {user_collected_content.external_id}"
            )

        # Fetch subtitle data
        subtitle_data = (
            self.youtube_content_ephemeral_repository.get_all_clean_subtitle_file_data(
                video_id=user_collected_content.external_id
            )
        )

        # Select best subtitle
        selected_subtitle = self.subtitle_utils.select_best_subtitle(
            subtitle_data, youtube_video_details
        )

        # Generate required content using AI Agent
        generated_data = (
            await self.required_content_generator_agent.generate_required_content(
                youtube_video_details=youtube_video_details,
                subtitle_map=selected_subtitle,
            )
        )

        # Create a generated content model
        generated_content_id = str(uuid.uuid4())
        generated_content = GeneratedContent(
            id=generated_content_id,
            external_id=user_collected_content.external_id,
            content_type=ContentType.YOUTUBE_VIDEO,
            generated={
                OutputType.VERY_SHORT: generated_data[OutputType.VERY_SHORT],
                OutputType.SHORT: generated_data[OutputType.SHORT],
            },
            status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
            status_details=[
                StatusDetail(
                    status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
                    created_at=datetime.utcnow(),
                    reason="Initial generation from automated flow.",
                )
            ],
            content_generated_at=youtube_video_details.release_date,
        )

        # Save to repository
        self.generated_content_repository.add_generated_content(
            generated_content=generated_content
        )

        self.logger.info(
            f"✅ Successfully generated required content for {user_collected_content.external_id}. "
            f"GeneratedContent ID: {generated_content_id}"
        )

        # Aggregate CategorizeGeneratedYoutubeContentCommand
        keys = [AggregatedScheduleService.GLOBAL_KEY]
        schedule_name = CategorizeGeneratedYoutubeContentAggregationCommand.ACTION_NAME

        schedule_data = await self.aggregated_schedule_service.get_active_schedule(
            schedule_name, keys
        )

        if schedule_data:
            # Cast to the command directly and update it
            command = (
                CategorizeGeneratedYoutubeContentAggregationCommand.model_validate(
                    schedule_data.payload
                )
            )
            command.payload.generated_content_ids.append(generated_content_id)
            await self.aggregated_schedule_service.update_scheduled_command(
                schedule_data.id, command
            )
        else:
            # Create the initial business command
            business_command = CategorizeGeneratedYoutubeContentAggregationCommand(
                payload=CategorizeGeneratedYoutubeContentAggregationPayload(
                    generated_content_ids=[generated_content_id],
                )
            )

            # Create new schedule
            await self.aggregated_schedule_service.create_schedule(
                keys=keys,
                command=business_command,
                delay_minutes=5,
            )

        self.logger.info(
            f"✅ Aggregated CategorizeGeneratedYoutubeContentAggregationCommand for generated_content_id: {generated_content_id}"
        )

        return generated_content_id
