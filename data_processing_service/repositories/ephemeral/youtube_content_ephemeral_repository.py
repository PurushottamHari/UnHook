"""
Abstract base class for youtube content ephemeral storage.
"""

from abc import ABC, abstractmethod
from typing import List

from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentSubStatus, ContentType, UserCollectedContent)
from data_processing_service.models.youtube.subtitle_data import SubtitleData


class YoutubeContentEphemeralRepository(ABC):
    @abstractmethod
    def store_subtitles(
        self,
        video_id: str,
        subtitles: str,
        extension: str,
        subtitle_type: str,
        language: str,
    ):
        pass

    @abstractmethod
    def store_clean_subtitles(
        self,
        video_id: str,
        subtitles: str,
        extension: str,
        subtitle_type: str,
        language: str,
    ):
        pass

    @abstractmethod
    def do_any_subtitles_exist_for_video(self, video_id: str) -> bool:
        pass

    @abstractmethod
    def do_any_clean_subtitles_exist_for_video(self, video_id: str) -> bool:
        pass

    @abstractmethod
    def check_if_downloaded_subtitle_file_exists(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> bool:
        pass

    @abstractmethod
    def check_if_clean_subtitle_file_exists(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> bool:
        pass

    @abstractmethod
    def get_downloaded_subtitle_file_data(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> str:
        pass

    @abstractmethod
    def get_clean_subtitle_file_data(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> str:
        pass

    @abstractmethod
    def get_all_clean_subtitle_file_data(self, video_id: str) -> SubtitleData:
        pass
