import os

from data_processing_service.models.youtube.subtitle_data import (SubtitleData,
                                                                  SubtitleMap)
from data_processing_service.repositories.ephemeral.youtube_content_ephemeral_repository import \
    YoutubeContentEphemeralRepository


class LocalYoutubeContentEphemeralRepository(YoutubeContentEphemeralRepository):
    """
    Local implementation of YoutubeContentEphemeralRepository that stores subtitles on the local filesystem.
    """

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "temp", "youtube"
            )
        self.subtitles_dir = os.path.join(base_dir, "subtitles")

    def _generate_subtitle_file_path(
        self,
        video_id: str,
        subtitle_type: str,
        extension: str,
        base_filename: str,
        language: str,
    ) -> str:
        """
        Generates the full file path for a subtitle file.
        """
        return os.path.join(
            self.subtitles_dir,
            video_id,
            subtitle_type,
            language,
            extension,
            f"{base_filename}.{extension}",
        )

    def store_subtitles(
        self,
        video_id: str,
        subtitles: str,
        extension: str,
        subtitle_type: str,
        language: str,
    ):
        """
        Stores the downloaded subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(
            video_id, subtitle_type, extension, "downloaded_subtitle", language
        )
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(subtitles)

    def store_clean_subtitles(
        self,
        video_id: str,
        subtitles: str,
        extension: str,
        subtitle_type: str,
        language: str,
    ):
        """
        Stores the cleaned subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(
            video_id, subtitle_type, extension, "clean_subtitles", language
        )
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(subtitles)

    def get_clean_subtitle_file_data(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> str:
        """
        Gets the cleaned subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(
            video_id, subtitle_type, extension, "clean_subtitles", language
        )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Validate file content
            if not content or not content.strip():
                raise RuntimeError(
                    f"Empty or whitespace-only subtitle file at {file_path}"
                )

            # Check for malformed content (single line with no breaks)
            if len(content.splitlines()) == 0 and len(content) > 1000:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Potentially malformed subtitle file at {file_path}: single line with {len(content)} characters"
                )

            return content
        except FileNotFoundError:
            raise RuntimeError(f"File not found at {file_path}")
        except UnicodeDecodeError as e:
            raise RuntimeError(
                f"Unicode decode error reading file at {file_path}: {str(e)}"
            )

    def get_downloaded_subtitle_file_data(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> str:
        """
        Gets the cleaned subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(
            video_id, subtitle_type, extension, "downloaded_subtitle", language
        )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"File not found at {file_path}")

    def do_any_subtitles_exist_for_video(self, video_id: str) -> bool:
        """
        Checks if any downloaded subtitles exist for a given video ID.
        """
        return self.check_files_exist(video_id, "downloaded_subtitle")

    def do_any_clean_subtitles_exist_for_video(self, video_id: str) -> bool:
        """
        Checks if any cleaned subtitles exist for a given video ID.
        """
        return self.check_files_exist(video_id, "clean_subtitles")

    def check_files_exist(self, video_id: str, base_filename: str) -> bool:
        """
        Checks for the existence of subtitle files, deleting any that are empty.
        """
        found_valid_file = False
        for subtitle_type in ["automatic", "manual"]:
            for language in ["en", "hi"]:
                video_subtitle_language_path = os.path.join(
                    self.subtitles_dir, video_id, subtitle_type, language
                )
                if not os.path.isdir(video_subtitle_language_path):
                    continue
                for extension in os.listdir(video_subtitle_language_path):
                    extension_path = os.path.join(
                        video_subtitle_language_path, extension
                    )
                    if os.path.isdir(extension_path):
                        file_path = self._generate_subtitle_file_path(
                            video_id, subtitle_type, extension, base_filename, language
                        )
                        if os.path.isfile(file_path):
                            if os.path.getsize(file_path) > 0:
                                found_valid_file = True
                            else:
                                os.remove(file_path)

        return found_valid_file

    def check_if_downloaded_subtitle_file_exists(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> bool:
        """
        Checks if a specific downloaded subtitle file exists and is not empty.
        """
        file_path = self._generate_subtitle_file_path(
            video_id, subtitle_type, extension, "downloaded_subtitle", language
        )
        return os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    def check_if_clean_subtitle_file_exists(
        self, video_id: str, extension: str, subtitle_type: str, language: str
    ) -> bool:
        """
        Checks if a specific clean subtitle file exists and is not empty.
        """
        file_path = self._generate_subtitle_file_path(
            video_id, subtitle_type, extension, "clean_subtitles", language
        )
        return os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    def get_all_clean_subtitle_file_data(self, video_id: str) -> SubtitleData:
        """
        Gets all clean subtitle file data for a video, returning a SubtitleData object
        with both automatic and manual subtitle mappings for all available languages.
        """
        automatic_subtitle_maps = []
        manual_subtitle_maps = []

        # Check for automatic subtitles
        for language in ["en", "hi"]:
            video_automatic_path = os.path.join(
                self.subtitles_dir, video_id, "automatic", language
            )
            if os.path.isdir(video_automatic_path):
                for extension in os.listdir(video_automatic_path):
                    extension_path = os.path.join(video_automatic_path, extension)
                    if os.path.isdir(extension_path):
                        file_path = self._generate_subtitle_file_path(
                            video_id,
                            "automatic",
                            extension,
                            "clean_subtitles",
                            language,
                        )
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                            with open(file_path, "r", encoding="utf-8") as f:
                                subtitle_content = f.read()
                            automatic_subtitle_maps.append(
                                SubtitleMap(
                                    language=language, subtitle=subtitle_content
                                )
                            )

        # Check for manual subtitles
        for language in ["en", "hi"]:
            video_manual_path = os.path.join(
                self.subtitles_dir, video_id, "manual", language
            )
            if os.path.isdir(video_manual_path):
                for extension in os.listdir(video_manual_path):
                    extension_path = os.path.join(video_manual_path, extension)
                    if os.path.isdir(extension_path):
                        file_path = self._generate_subtitle_file_path(
                            video_id, "manual", extension, "clean_subtitles", language
                        )
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                            with open(file_path, "r", encoding="utf-8") as f:
                                subtitle_content = f.read()
                            manual_subtitle_maps.append(
                                SubtitleMap(
                                    language=language, subtitle=subtitle_content
                                )
                            )

        return SubtitleData(
            automatic=automatic_subtitle_maps, manual=manual_subtitle_maps
        )
