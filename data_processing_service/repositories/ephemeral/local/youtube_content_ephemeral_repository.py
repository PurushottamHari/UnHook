import os
from data_processing_service.repositories.ephemeral.youtube_content_ephemeral_repository import YoutubeContentEphemeralRepository

class LocalYoutubeContentEphemeralRepository(YoutubeContentEphemeralRepository):
    """
    Local implementation of YoutubeContentEphemeralRepository that stores subtitles on the local filesystem.
    """
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "youtube")
        self.subtitles_dir = os.path.join(base_dir, "subtitles")

    def _generate_subtitle_file_path(self, video_id: str, subtitle_type: str, extension: str, base_filename: str, language: str) -> str:
        """
        Generates the full file path for a subtitle file.
        """
        return os.path.join(self.subtitles_dir, video_id, subtitle_type, language, extension, f"{base_filename}.{extension}")

    def store_subtitles(self, video_id: str, subtitles: str, extension: str, subtitle_type: str, language: str):
        """
        Stores the downloaded subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, "downloaded_subtitle", language)
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(subtitles)

    def store_clean_subtitles(self, video_id: str, subtitles: str, extension: str, subtitle_type: str, language: str):
        """
        Stores the cleaned subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, "clean_subtitles", language)
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(subtitles)

    def get_clean_subtitle_file_data(self, video_id: str, extension: str, subtitle_type: str, language: str) -> str:
        """
        Gets the cleaned subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, "clean_subtitles", language)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"File not found at {file_path}")
    def get_downloaded_subtitle_file_data(self, video_id: str, extension: str, subtitle_type: str, language: str) -> str:
        """
        Gets the cleaned subtitles for a video.
        """
        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, "downloaded_subtitle", language)
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
        for subtitle_type in ['automatic', 'manual']:
            for language in ['en', 'hi']:
                video_subtitle_language_path = os.path.join(self.subtitles_dir, video_id, subtitle_type, language)
                if not os.path.isdir(video_subtitle_language_path):
                    continue
                for extension in os.listdir(video_subtitle_language_path):
                    extension_path = os.path.join(video_subtitle_language_path, extension)
                    if os.path.isdir(extension_path):
                        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, base_filename, language)
                        if os.path.isfile(file_path):
                            if os.path.getsize(file_path) > 0:
                                found_valid_file = True
                            else:
                                os.remove(file_path)

        return found_valid_file

    def check_if_downloaded_subtitle_file_exists(self, video_id: str, extension: str, subtitle_type: str, language: str) -> bool:
        """
        Checks if a specific downloaded subtitle file exists and is not empty.
        """
        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, "downloaded_subtitle", language)
        return os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    def check_if_clean_subtitle_file_exists(self, video_id: str, extension: str, subtitle_type: str, language: str) -> bool:
        """
        Checks if a specific clean subtitle file exists and is not empty.
        """
        file_path = self._generate_subtitle_file_path(video_id, subtitle_type, extension, "clean_subtitles", language)
        return os.path.isfile(file_path) and os.path.getsize(file_path) > 0
