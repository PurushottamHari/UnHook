import json
import logging
import re

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.youtube.subtitle_models import (
    SubtitleData, SubtitleMap)
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoDetails

logger = logging.getLogger(__name__)


@injectable()
class SubtitleUtils:
    """A class for managing and cleaning subtitle files (Logic only)."""

    def __init__(self):
        self.SUBTITLE_PRIORITY_LIST = ["srt", "vtt", "json3"]

    def select_best_subtitle(
        self, subtitle_data: SubtitleData, youtube_video_details: YouTubeVideoDetails
    ) -> SubtitleMap:
        """
        Select the best subtitle based on language and manual/automatic preference.
        Args:
            subtitle_data: SubtitleData object containing manual and automatic subtitles
            youtube_video_details: YouTubeVideoDetails object (should have a 'language' attribute)
        Returns:
            SubtitleMap: The selected subtitle map
        """
        preferred_language = youtube_video_details.language or "en"

        # 1. Prefer manual subtitle in preferred language
        for sub in subtitle_data.manual:
            if (
                sub.language.lower() == preferred_language.lower()
                and sub.subtitle.strip()
            ):
                return sub
        # 2. Prefer automatic subtitle in preferred language
        for sub in subtitle_data.automatic:
            if (
                sub.language.lower() == preferred_language.lower()
                and sub.subtitle.strip()
            ):
                return sub
        # 3. Any manual subtitle
        for sub in subtitle_data.manual:
            if sub.subtitle.strip():
                return sub
        # 4. Any automatic subtitle
        for sub in subtitle_data.automatic:
            if sub.subtitle.strip():
                return sub
        # 5. If nothing is available, raise an error or return a dummy SubtitleMap
        raise ValueError("No subtitles available to select.")
