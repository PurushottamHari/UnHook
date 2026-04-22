import logging

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging.aggregated_schedule import AggregatedScheduleService
from data_collector_service.config.config import Config
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.messaging.models.commands import (
    EnrichYouTubeVideoForUserCommand,
    ProcessYoutubeChannelRejectionAggregationCommand,
    ProcessYoutubeChannelRejectionAggregationPayload)
from data_collector_service.messaging.redis.producer import \
    RedisMessageProducer
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoStatus
from data_collector_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository
from data_collector_service.services.collection.collectors.youtube.tools.youtube_external_tool import \
    YouTubeExternalTool

logger = logging.getLogger(__name__)


@injectable()
class EnrichYouTubeVideoContentService:
    """Service for enriching YouTube video details with extra metadata."""

    @inject
    def __init__(
        self,
        youtube_repository: YouTubeCollectedContentRepository,
        youtube_tool: YouTubeExternalTool,
        message_producer: RedisMessageProducer,
        user_service_client: UserServiceClient,
        aggregated_schedule_service: AggregatedScheduleService,
        config: Config,
    ):
        """
        Initialize the enrichment service.

        Args:
            youtube_repository: Repository for managing raw YouTube content
            youtube_tool: External tool for YouTube interactions
            message_producer: Producer to send commands to the queue
        """
        self.youtube_repository = youtube_repository
        self.youtube_tool = youtube_tool
        self.message_producer = message_producer
        self.user_service_client = user_service_client
        self.aggregated_schedule_service = aggregated_schedule_service
        self.config = config

    async def enrich_video(
        self,
        video_id: str,
        user_id: str,
        user_collected_content_id: str,
        channel_name: str,
    ) -> None:
        """
        Enrich a YouTube video's metadata and update its status.

        Args:
            video_id: The YouTube video ID
            user_id: The ID of the user requesting enrichment
        """
        logger.info(
            f"🎬 [EnrichYouTubeVideoContentService] Enriching video {video_id} for user {user_id}"
        )

        # Ensure user exists before proceeding
        user = await self.user_service_client.get_user(user_id)
        if not user:
            logger.error(
                f"❌ [EnrichYouTubeVideoContentService] User {user_id} not found. Aborting enrichment for video {video_id}."
            )
            return

        # fetch the youtube video details with the id
        try:
            video = self.youtube_repository.get_video_by_id(video_id)
        except ValueError as e:
            logger.error(f"Video {video_id} not found: {e}")
            raise

        # Only proceed to fetch more data if status is collected
        # If status is enriched or subtitles_stored skip this step
        if video.status == YouTubeVideoStatus.COLLECTED:
            # Fetch data and enrich using YouTubeExternalTool
            enriched_videos = self.youtube_tool.enrich_video_data_with_details([video])
            if not enriched_videos:
                logger.warning(f"⚠️ No enrichment data found for video {video_id}")
                # Todo: Puru this needs to be a retry or a dead letter queue scenario
                return
            enriched_video = enriched_videos[0]
            enriched_video.set_status(
                YouTubeVideoStatus.ENRICHED, "Video metadata enriched via external tool"
            )
            enriched_video.version += 1
            self.youtube_repository.upsert_videos([enriched_video])
            logger.info(f"✅ Video {video_id} enriched and updated in repository")

        elif video.status in [
            YouTubeVideoStatus.ENRICHED,
            YouTubeVideoStatus.SUBTITLES_STORED,
        ]:
            logger.info(
                f"⏭️ Video {video_id} already has status '{video.status}'. Skipping enrichment."
            )
            enriched_video = video

        else:
            error_msg = f"❌ Unexpected status '{video.status}' for video {video_id}. Expected '{YouTubeVideoStatus.COLLECTED}'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        keys = [user_id, channel_name]

        # Use the command's action name as the schedule name for consistency
        schedule_name = ProcessYoutubeChannelRejectionAggregationCommand.ACTION_NAME

        schedule_data = await self.aggregated_schedule_service.get_active_schedule(
            schedule_name, keys
        )

        if schedule_data:
            # Cast to the command directly and update it
            command = ProcessYoutubeChannelRejectionAggregationCommand.model_validate(
                schedule_data.payload
            )
            command.payload.user_collected_content_ids.append(user_collected_content_id)
            await self.aggregated_schedule_service.update_scheduled_command(
                schedule_data.id, command
            )
        else:
            # Create the initial business command
            business_command = ProcessYoutubeChannelRejectionAggregationCommand(
                payload=ProcessYoutubeChannelRejectionAggregationPayload(
                    user_id=user_id,
                    channel_name=channel_name,
                    user_collected_content_ids=[user_collected_content_id],
                )
            )

            # Create new schedule using the specialized model
            await self.aggregated_schedule_service.create_schedule(
                keys=keys,
                command=business_command,
                delay_minutes=1,
                topic=self.config.messaging_command_topic,
            )

        logger.info(
            f"🚀 Video {video_id} enrichment workflow complete. Ready for next phase."
        )
