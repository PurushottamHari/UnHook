"""
Service for processing subtitles for YouTube content.
"""

import logging

from data_collector_service.collectors.youtube.models import YouTubeVideoDetails
from data_collector_service.collectors.youtube.tools.youtube_external_tool import (
    YouTubeExternalTool,
)
from data_collector_service.models.user_collected_content import (
    ContentType,
    UserCollectedContent,
)
from data_processing_service.repositories.ephemeral.local.youtube_content_ephemeral_repository import (
    LocalYoutubeContentEphemeralRepository,
)
from data_processing_service.repositories.ephemeral.youtube_content_ephemeral_repository import (
    YoutubeContentEphemeralRepository,
)
from data_processing_service.services.processing.youtube.subtitles.utils.subtitle_utils import (
    SubtitleUtils,
)


class ProcessSubtitlesForYoutubeContent:
    """Service for processing subtitles for YouTube content."""

    def __init__(self):
        """Initialize the subtitle processor."""
        self.logger = logging.getLogger(__name__)
        self.youtube_content_ephemeral_repository: YoutubeContentEphemeralRepository = (
            LocalYoutubeContentEphemeralRepository()
        )
        self.SUBTITLE_PRIORITY_LIST = ["srt", "vtt", "json3"]
        self.subtitle_utils = SubtitleUtils()
        self.youtube_external_tool = YouTubeExternalTool()

    def process_subtitles(self, content: UserCollectedContent) -> bool:
        """
        Process subtitles for a given YouTube content.

        Args:
            content: The YouTube content to process subtitles for

        Returns:
            bool: True if subtitles were successfully processed, False otherwise
        """
        try:
            # Check if the download is present in the ephemeral storage, else continue
            video_details = content.data.get(ContentType.YOUTUBE_VIDEO)
            if self._is_subtitle_stored(video_details):
                self.logger.info(
                    f"Subtitles already downloaded for content ID: {content.id}"
                )
            else:
                # Download the subtitles
                if not self._download_and_store_subtitles(video_details):
                    self.logger.warning(
                        f"Failed to download subtitles for content ID: {content.id}"
                    )
                    return False

            # Check if clean subtitles have already been stored, else continue
            if self._is_clean_subtitles_stored(video_details):
                self.logger.info(
                    f"Clean subtitles already stored for content ID: {content.id}"
                )
            else:
                # Clean the subtitles and store them in the ephemeral storage
                if not self._clean_and_store_subtitles(video_details):
                    self.logger.warning(
                        f"Failed to clean and store subtitles for content ID: {content.id}"
                    )
                    return False

            return True

        except Exception as e:
            self.logger.error(
                f"Error processing subtitles for content ID {content.id}: {str(e)}"
            )
            return False

    def _is_subtitle_stored(self, content: YouTubeVideoDetails) -> bool:
        """
        Check if subtitles are already downloaded for the content.

        Args:
            content: The YouTube content to check

        Returns:
            bool: True if subtitles are downloaded, False otherwise
        """
        return (
            self.youtube_content_ephemeral_repository.do_any_subtitles_exist_for_video(
                content.video_id
            )
        )

    def _download_and_store_subtitles(self, content: YouTubeVideoDetails) -> bool:
        """
        Download subtitles for the given content.

        Args:
            content: The YouTube content to download subtitles for

        Returns:
            bool: True if download was successful, False otherwise
        """
        if not content.subtitles.automatic and not content.subtitles.manual:
            raise RuntimeError("WTF one was supposed to be there!")

        # Todo: Puru Use AI to determine if automatic is better or manual?

        # get latest subtitle data for the video
        enriched_video_data_list = (
            self.youtube_external_tool.enrich_video_data_with_details(
                youtube_video_details=[content]
            )
        )
        enriched_video_data = enriched_video_data_list[0]
        found_automatic_subtitle = False
        if enriched_video_data.subtitles.automatic:
            subtitle_data = enriched_video_data.subtitles.automatic
            for lang in ["en", "hi"]:
                if subtitle_data.get(lang):
                    subtitle_lang_data = subtitle_data.get(lang)
                    for ext in self.SUBTITLE_PRIORITY_LIST:
                        if subtitle_lang_data.get(ext):
                            try:
                                url = subtitle_lang_data.get(ext)
                                subtitle_content = (
                                    self.subtitle_utils.download_subtitle_file(url)
                                )
                                self.youtube_content_ephemeral_repository.store_subtitles(
                                    video_id=enriched_video_data.video_id,
                                    subtitles=subtitle_content,
                                    extension=ext,
                                    subtitle_type="automatic",
                                    language=lang,
                                )
                                found_automatic_subtitle = True
                                break
                            except Exception as e:
                                continue

        found_manual_subtitle = False
        if enriched_video_data.subtitles.manual:
            subtitle_data = enriched_video_data.subtitles.automatic
            for lang in ["en", "hi"]:
                if subtitle_data.get(lang):
                    subtitle_lang_data = subtitle_data.get(lang)
                    for ext in self.SUBTITLE_PRIORITY_LIST:
                        if subtitle_lang_data.get(ext):
                            try:
                                url = subtitle_lang_data.get(ext)
                                subtitle_content = (
                                    self.subtitle_utils.download_subtitle_file(url)
                                )
                                self.youtube_content_ephemeral_repository.store_subtitles(
                                    video_id=enriched_video_data.video_id,
                                    subtitles=subtitle_content,
                                    extension=ext,
                                    subtitle_type="manual",
                                    language=lang,
                                )
                                found_manual_subtitle = True
                                break
                            except Exception as e:
                                continue

        return found_automatic_subtitle or found_manual_subtitle

    def _is_clean_subtitles_stored(self, content: YouTubeVideoDetails) -> bool:
        """
        Check if clean subtitles are already stored for the content.

        Args:
            content: The YouTube content to check

        Returns:
            bool: True if clean subtitles are stored, False otherwise
        """
        return self.youtube_content_ephemeral_repository.do_any_clean_subtitles_exist_for_video(
            content.video_id
        )

    def _clean_and_store_subtitles(self, content: YouTubeVideoDetails) -> bool:
        """
        Clean subtitles and store them in ephemeral storage.

        Args:
            content: The YouTube content to clean and store subtitles for

        Returns:
            bool: True if cleaning and storing was successful, False otherwise
        """
        generated_clean_subtitles = False
        for lan in ["en", "hi"]:
            for subtitle_type in ["automatic", "manual"]:
                for ext in self.SUBTITLE_PRIORITY_LIST:
                    if self.youtube_content_ephemeral_repository.check_if_downloaded_subtitle_file_exists(
                        video_id=content.video_id,
                        subtitle_type=subtitle_type,
                        extension=ext,
                        language=lan,
                    ):
                        subtitle_content = self.youtube_content_ephemeral_repository.get_downloaded_subtitle_file_data(
                            video_id=content.video_id,
                            subtitle_type=subtitle_type,
                            extension=ext,
                            language=lan,
                        )
                        if subtitle_content:
                            cleaned_subtitles = self.subtitle_utils.clean_subtitles(
                                subtitle_content, ext
                            )
                            if cleaned_subtitles:
                                self.youtube_content_ephemeral_repository.store_clean_subtitles(
                                    video_id=content.video_id,
                                    subtitles=cleaned_subtitles,
                                    language=lan,
                                    subtitle_type=subtitle_type,
                                    extension=ext,
                                )
                                generated_clean_subtitles = True
                                self.logger.info(
                                    f"Successfully cleaned and stored {subtitle_type} subtitles with extension {ext} for video {content.video_id}"
                                )

        if not generated_clean_subtitles:
            self.logger.warning(
                f"Could not find any subtitles to clean for video {content.video_id}"
            )
        return generated_clean_subtitles
