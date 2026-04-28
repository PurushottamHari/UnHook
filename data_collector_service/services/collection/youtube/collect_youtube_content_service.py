import logging
from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.messaging.models.commands import (
    EnrichYouTubeVideoForUserCommand, EnrichYouTubeVideoForUserPayload)
from data_collector_service.messaging.redis.producer import \
    RedisMessageProducer
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoStatus
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from data_collector_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository
from data_collector_service.services.collection.collectors.youtube.adapters.youtube_to_user_content_adapter import \
    YouTubeToUserContentAdapter
from data_collector_service.services.collection.collectors.youtube.tools.youtube_external_tool import \
    YouTubeExternalTool

logger = logging.getLogger(__name__)


@injectable()
class CollectYouTubeContentService:
    """Service for collecting content from a specific YouTube channel for a user."""

    @inject
    def __init__(
        self,
        user_repository: UserCollectedContentRepository,
        youtube_repository: YouTubeCollectedContentRepository,
        youtube_tool: YouTubeExternalTool,
        adapter: YouTubeToUserContentAdapter,
        message_producer: RedisMessageProducer,
        user_service_client: UserServiceClient,
    ):
        """
        Initialize the YouTube content collection service.

        Args:
            user_repository: Repository for managing user collected content
            youtube_repository: Repository for managing raw YouTube content
            youtube_tool: External tool for YouTube interactions
            adapter: Adapter for converting YouTube data to user content
            message_producer: Producer to send commands to the queue
            config: Application configuration
        """
        self.user_repository = user_repository
        self.youtube_repository = youtube_repository
        self.youtube_tool = youtube_tool
        self.adapter = adapter
        self.message_producer = message_producer
        self.user_service_client = user_service_client

    async def collect_channel(
        self, user_id: str, channel_id: str, max_videos: int
    ) -> None:
        """
        Collect content from a specific YouTube channel.

        Args:
            user_id: The ID of the user
            channel_id: The YouTube channel ID
            max_videos: Maximum number of videos to fetch
        """
        logger.info(
            f"🎬 [CollectYouTubeContentService] Collecting channel {channel_id} for user {user_id}"
        )

        # Ensure user exists before proceeding
        user = await self.user_service_client.get_user(user_id)
        if not user:
            logger.error(
                f"❌ [CollectYouTubeContentService] User {user_id} not found. Aborting collection for channel {channel_id}."
            )
            return

        # Todo: Puru Have a global config which makes sure that one channel search is not bombarded unneccessarily

        # Fetch latest videos from YouTube
        latest_videos = self.youtube_tool.find_latest_videos(
            channel_name=channel_id, max=max_videos
        )

        if not latest_videos:
            logger.info(f"No videos found for channel {channel_id}")
            return

        # Extract video IDs
        latest_video_ids = [video.video_id for video in latest_videos]

        # Filter out videos already in the raw shared collection (from any user)
        uncollected_globally_video_ids = self.youtube_repository.filter_existing_videos(
            latest_video_ids
        )

        globally_new_videos = [
            video
            for video in latest_videos
            if video.video_id in uncollected_globally_video_ids
        ]

        if globally_new_videos:
            # Save raw video data to the shared collection (only for globally new videos)
            logger.info(
                f"Saving {len(globally_new_videos)} globally new videos to the shared collection"
            )
            self.youtube_repository.upsert_videos(globally_new_videos)

        # Filter out already collected videos
        uncollected_user_video_ids = (
            self.user_repository.filter_already_collected_content(
                user_id, latest_video_ids
            )
        )

        if not uncollected_user_video_ids:
            logger.info(
                f"No new videos found for channel {channel_id} for user {user_id}"
            )
            return

        # Create UserCollectedContent models for all uncollected videos
        videos_to_collect = [
            video
            for video in latest_videos
            if video.video_id in uncollected_user_video_ids
        ]

        user_content_list = self.adapter.convert_batch(
            videos_to_collect, user_id, include_data=False
        )

        # Upsert all in one shot
        logger.info(
            f"📥 [CollectYouTubeContentService] Upserting {len(user_content_list)} videos for user {user_id}"
        )
        self.user_repository.upsert_user_collected_content_batch(user_content_list)

        # Todo: Puru Existing bug which is that if the previous upsert passes but the commands being sent out fail, we would need to still send out the commands in the retry.
        # The solve for this is to filter out the user collected content in collected status as well and resend the commands.
        commands_to_send = []
        for user_content in user_content_list:
            payload = EnrichYouTubeVideoForUserPayload(
                user_id=user_id,
                video_id=user_content.external_id,
                user_collected_content_id=user_content.id,
                channel_name=channel_id,
            )
            command = EnrichYouTubeVideoForUserCommand(payload=payload)
            commands_to_send.append(command)

        if commands_to_send:
            await self.message_producer.send_commands(commands_to_send)
            logger.info(
                f"✅ Enqueued {len(commands_to_send)} collection commands for user {user_id}"
            )
