import logging

from user_service.models.user import User

from ...repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from ..base_static import BaseStaticCollector
from .adapters.youtube_to_user_content_adapter import \
    YouTubeToUserContentAdapter
from .tools.youtube_external_tool import YouTubeExternalTool

logger = logging.getLogger(__name__)


class YouTubeStaticCollector(BaseStaticCollector):
    """YouTube-specific implementation of static data collection."""

    def __init__(self, user_repository: UserCollectedContentRepository):
        """
        Initialize the YouTube static collector.

        Args:
            user_repository: Repository for managing user collected content
        """
        self.youtube_tool = YouTubeExternalTool()
        self.user_repository = user_repository
        self.adapter = YouTubeToUserContentAdapter()

    def collect(self, user: User) -> None:
        """
        Collect static data from YouTube for the given user.

        Args:
            user: User object containing user configuration and preferences
        """
        youtube_config = user.manual_configs.youtube
        channels = youtube_config.channels

        for channel in channels:
            channel_name = channel.channel_id
            max_videos = channel.max_videos_daily

            # Step 1: Get latest videos from YouTube
            latest_videos = self.youtube_tool.find_latest_videos(
                channel_name=channel_name, max=max_videos
            )
            if not latest_videos:
                logger.info(f"No videos found for channel {channel_name}")
                continue

            # Extract video IDs as a list of strings
            latest_video_ids = [video.video_id for video in latest_videos]

            # Step 2: Filter out already collected videos
            user_id = str(user.id)
            uncollected_video_ids = (
                self.user_repository.filter_already_collected_content(
                    user_id, latest_video_ids
                )
            )

            uncollected_videos = [
                video
                for video in latest_videos
                if video.video_id in uncollected_video_ids
            ]
            if not uncollected_videos:
                logger.info(f"No uncollected videos found for channel {channel_name}")
                continue
            # Enrich this data with more input such as release_date,tags etc
            enriched_uncollected_videos = (
                self.youtube_tool.enrich_video_data_with_details(
                    youtube_video_details=uncollected_videos
                )
            )

            # Step 3: Convert videos to user collected content and add to user's history
            user_collected_content = self.adapter.convert_batch(
                enriched_uncollected_videos, user_id
            )
            self.user_repository.add_collected_videos(user_collected_content, user_id)
