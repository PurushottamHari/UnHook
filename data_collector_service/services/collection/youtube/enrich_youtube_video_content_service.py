import logging

from injector import inject

from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.infra.dependency_injection.injectable import \
    injectable
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

    async def enrich_video(
        self, video_id: str, user_id: str, user_collected_content_id: str
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
        user = self.user_service_client.get_user(user_id)
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
        # Any other status error out
        if video.status == YouTubeVideoStatus.COLLECTED:
            # Fetch data and enrich using YouTubeExternalTool
            # The tool expects a list of YouTubeVideoDetails
            enriched_videos = self.youtube_tool.enrich_video_data_with_details([video])
            if not enriched_videos:
                logger.warning(f"⚠️ No enrichment data found for video {video_id}")
                return
            enriched_video = enriched_videos[0]
            # update the youtube video details now with the enriched data to enriched
            enriched_video.set_status(
                YouTubeVideoStatus.ENRICHED, "Video metadata enriched via external tool"
            )
            enriched_video.version += 1
            # upsert to repository if something done
            self.youtube_repository.upsert_videos([enriched_video])
            logger.info(f"✅ Video {video_id} enriched and updated in repository")

        elif video.status in [
            YouTubeVideoStatus.ENRICHED,
            YouTubeVideoStatus.SUBTITLES_STORED,
        ]:
            logger.info(
                f"⏭️ Video {video_id} already has status '{video.status}'. Skipping enrichment."
            )

        else:
            error_msg = f"❌ Unexpected status '{video.status}' for video {video_id}. Expected '{YouTubeVideoStatus.COLLECTED}'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # keep a section to generate a message for the next step (ill define it later)....keep the publisher injection ready though
        # TODO: Implement next step command generation (e.g., subtitle extraction)
        # payload = SomeNextStepPayload(video_id=video_id, user_id=user_id)
        # command = SomeNextStepCommand(payload=payload)
        # await self.message_producer.send_commands(topic, [command])

        logger.info(
            f"🚀 Video {video_id} enrichment workflow complete. Ready for next phase."
        )
