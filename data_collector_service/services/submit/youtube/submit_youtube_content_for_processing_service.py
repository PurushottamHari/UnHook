import logging

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.user_collected_content import (
    ContentSubStatus, UserCollectedContent)
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoStatus
from data_collector_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository
from data_collector_service.services.collection.collectors.youtube.tools.utils.subtitle_utils import \
    SubtitleUtils

logger = logging.getLogger(__name__)


@injectable()
class SubmitYoutubeContentForProcessingService:
    """Service for processing YouTube specific content during submission."""

    @inject
    def __init__(
        self,
        youtube_repository: YouTubeCollectedContentRepository,
        subtitle_utils: SubtitleUtils,
    ):
        self.youtube_repository = youtube_repository
        self.subtitle_utils = subtitle_utils

    async def process_youtube_subtitles(self, content: UserCollectedContent) -> None:
        """Logic for downloading and storing subtitles using SubtitleUtils."""
        video_id = content.external_id

        # Fetch video details from YouTubeCollectedContentRepository
        try:
            video_details = self.youtube_repository.get_video_by_id(video_id)
        except ValueError as e:
            logger.error(f"Video {video_id} not found in repository: {e}")
            return

        if not video_details:
            logger.error(f"❌ No YouTube video details found for video {video_id}")
            raise ValueError(f"Video {video_id} not found in repository")

        if video_details.status == YouTubeVideoStatus.SUBTITLES_STORED:
            logger.info(f"Subtitles already downloaded for video {video_id}")
            return

        if video_details.status != YouTubeVideoStatus.ENRICHED:
            logger.error(
                f"❌ Video {video_id} is not in ENRICHED state. Cannot download subtitles"
            )
            raise ValueError(
                f"Video {video_id} is not in ENRICHED state. Cannot download subtitles"
            )

        # 1. Download subtitles if not already present
        if not self.subtitle_utils.ephemeral_repository.do_any_subtitles_exist_for_video(
            video_id
        ):
            logger.info(f"Downloading subtitles for video {video_id}")
            success = self.subtitle_utils.download_and_store_subtitles(video_details)
            if not success:
                logger.warning(f"Failed to download subtitles for video {video_id}")
                # Todo: Puru this a deadletter queue and retry logic usecase for the messaging pipeline
                return

        # 2. Clean and store subtitles if not already present
        if not self.subtitle_utils.ephemeral_repository.do_any_clean_subtitles_exist_for_video(
            video_id
        ):
            logger.info(f"Cleaning subtitles for video {video_id}")
            success = self.subtitle_utils.clean_and_store_subtitles(video_details)
            if not success:
                logger.warning(
                    f"Failed to clean and store subtitles for video {video_id}"
                )
                return

        # 3. Update YouTube video status in repository
        video_details.set_status(
            YouTubeVideoStatus.SUBTITLES_STORED, "Subtitles downloaded and cleaned"
        )
        video_details.version += 1
        self.youtube_repository.upsert_videos([video_details])

        # 4. Update sub-status in content
        content.set_sub_status(
            ContentSubStatus.SUBTITLES_STORED, "YouTube subtitles processed"
        )
