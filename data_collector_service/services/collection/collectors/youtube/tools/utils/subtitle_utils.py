"""
Utility for cleaning and managing subtitles.
"""

import json
import logging
import re
from typing import List, Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.youtube.subtitle_models import (
    SubtitleData, SubtitleMap)
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoDetails
from data_collector_service.repositories.youtube_content_ephemeral_repository import \
    YoutubeContentEphemeralRepository
from data_collector_service.services.collection.collectors.youtube.tools.youtube_external_tool import \
    YouTubeExternalTool

logger = logging.getLogger(__name__)


@injectable()
class SubtitleUtils:
    """A class for managing and cleaning subtitle files."""

    @inject
    def __init__(
        self,
        youtube_tool: YouTubeExternalTool,
        ephemeral_repository: YoutubeContentEphemeralRepository,
    ):
        self.youtube_tool = youtube_tool
        self.ephemeral_repository = ephemeral_repository
        self.SUBTITLE_PRIORITY_LIST = ["srt", "vtt", "json3"]

    def download_and_store_subtitles(self, video_details: YouTubeVideoDetails) -> bool:
        """Downloads and stores subtitles for a video."""
        if not video_details.subtitles or (
            not video_details.subtitles.automatic and not video_details.subtitles.manual
        ):
            logger.warning(
                f"No subtitle metadata available for video {video_details.video_id}"
            )
            return False

        candidates = self._get_candidates(video_details)
        if not candidates:
            logger.warning(
                f"No valid subtitle candidates found in metadata for video {video_details.video_id}"
            )
            return False

        # Try candidates (max 5)
        for i, (sub_type, lang, fmt) in enumerate(candidates[:5]):
            logger.info(
                f"Attempting subtitle download {i+1}/5: {sub_type} | {lang} | {fmt} for {video_details.video_id}"
            )
            try:
                subtitle_content = self.youtube_tool.download_subtitles(
                    video_details.video_id, lang, fmt, sub_type
                )

                if subtitle_content is None:
                    logger.warning(
                        f"Download returned None for {sub_type} | {lang} | {fmt}. Trying next candidate."
                    )
                    continue

                self.ephemeral_repository.store_subtitles(
                    video_id=video_details.video_id,
                    subtitles=subtitle_content,
                    extension=fmt,
                    subtitle_type=sub_type,
                    language=lang,
                )
                return True
            except Exception as e:
                logger.error(
                    f"Error downloading {sub_type} subtitles ({lang}, {fmt}) for {video_details.video_id}: {e}"
                )
                continue

        raise RuntimeError(
            f"Failed to download any subtitles for video {video_details.video_id} after trying {min(5, len(candidates))} candidates."
        )

    def _get_candidates(
        self, video_details: YouTubeVideoDetails
    ) -> List[tuple[str, str, str]]:
        """
        Generates a prioritized list of subtitle candidates based on enriched metadata.
        Returns a list of tuples: (sub_type, language, format)
        """
        candidates = []
        # Target languages: Video's specific language first, then generic English
        target_langs = [video_details.language or "en", "en"]
        fmt_priority = ["json3", "vtt", "srt"]

        for sub_type, subs_map in [
            ("manual", video_details.subtitles.manual),
            ("automatic", video_details.subtitles.automatic),
        ]:
            if not subs_map:
                continue

            # Priority 1: Exact matches or prefix matches for target languages
            for target in target_langs:
                for actual_lang in subs_map.keys():
                    if actual_lang.lower().startswith(target.lower()):
                        for fmt in fmt_priority:
                            if subs_map[actual_lang].get(fmt):
                                candidates.append((sub_type, actual_lang, fmt))

            # Priority 2: Fallback (Anything else available, in the order yt-dlp returned it)
            for actual_lang in subs_map.keys():
                if not any(
                    actual_lang.lower().startswith(t.lower()) for t in target_langs
                ):
                    for fmt in fmt_priority:
                        if subs_map[actual_lang].get(fmt):
                            candidates.append((sub_type, actual_lang, fmt))

        # Deduplicate while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def clean_and_store_subtitles(self, video_details: YouTubeVideoDetails) -> bool:
        """Cleans and stores subtitles for a video."""
        generated_clean_subtitles = False
        video_id = video_details.video_id

        for lan in ["en", "hi"]:
            for subtitle_type in ["automatic", "manual"]:
                for ext in self.SUBTITLE_PRIORITY_LIST:
                    if self.ephemeral_repository.check_if_downloaded_subtitle_file_exists(
                        video_id=video_id,
                        subtitle_type=subtitle_type,
                        extension=ext,
                        language=lan,
                    ):
                        subtitle_content = (
                            self.ephemeral_repository.get_downloaded_subtitle_file_data(
                                video_id=video_id,
                                subtitle_type=subtitle_type,
                                extension=ext,
                                language=lan,
                            )
                        )
                        if subtitle_content:
                            try:
                                cleaned_subtitles = self.clean_subtitles(
                                    subtitle_content, ext
                                )
                                if cleaned_subtitles and cleaned_subtitles.strip():
                                    self.ephemeral_repository.store_clean_subtitles(
                                        video_id=video_id,
                                        subtitles=cleaned_subtitles,
                                        language=lan,
                                        subtitle_type=subtitle_type,
                                        extension=ext,
                                    )
                                    generated_clean_subtitles = True
                            except Exception as e:
                                logger.error(
                                    f"Error cleaning subtitles for {video_id}: {e}"
                                )
                                continue
        return generated_clean_subtitles

    def clean_subtitles(self, subtitle_content: str, extension: str) -> str:
        """
        Cleans the subtitle content based on its format (extension).

        Args:
            subtitle_content: The raw subtitle content.
            extension: The extension of the subtitle file (e.g., 'srt', 'vtt', 'json3').

        Returns:
            The cleaned subtitle content as a single string.
        """
        if extension == "srt":
            return self._clean_srt(subtitle_content)
        elif extension == "vtt":
            return self._clean_vtt(subtitle_content)
        elif extension == "json3":
            return self._clean_json3(subtitle_content)
        else:
            # Default fallback for unknown formats
            raise RuntimeError("Subtitle file format unsupported: " + extension)

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

    def _clean_srt(self, content: str) -> str:
        """Cleans SRT subtitle content."""
        lines = content.splitlines()
        cleaned_lines = []
        for line in lines:
            # Skip sequence numbers (lines that are just digits)
            if re.match(r"^\d+$", line.strip()):
                continue
            # Skip timestamp lines
            if re.match(
                r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", line.strip()
            ):
                continue
            # Skip empty lines
            if line.strip() == "":
                continue
            cleaned_lines.append(line.strip())

        result = "\n".join(cleaned_lines)

        if not result.strip():
            return ""

        return result

    def _clean_vtt(self, content: str) -> str:
        """Cleans VTT subtitle content."""
        if content.startswith("WEBVTT"):
            header_end = content.find("\n\n")
            if header_end != -1:
                content = content[header_end + 2 :]
            else:
                content = "\n".join(content.splitlines()[1:])

        lines = content.splitlines()
        cleaned_lines = []
        prev_line = None
        for line in lines:
            if re.match(
                r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line
            ):
                continue
            if not line.strip():
                continue
            line = re.sub(r"<[^>]+>", "", line)
            if re.match(r"^\d+$", line.strip()):
                continue
            line = line.strip()
            if line and line != prev_line:
                cleaned_lines.append(line)
            prev_line = line
        return " ".join(cleaned_lines)

    def _clean_json3(self, content: str) -> str:
        """Cleans json3 subtitle content."""
        try:
            data = json.loads(content)
            text_segments = []
            if "events" in data:
                for event in data["events"]:
                    if "segs" in event:
                        for seg in event["segs"]:
                            if "utf8" in seg:
                                text_segments.append(seg["utf8"])
            return "".join(text_segments).replace("\n", " ").strip()
        except json.JSONDecodeError:
            return ""
