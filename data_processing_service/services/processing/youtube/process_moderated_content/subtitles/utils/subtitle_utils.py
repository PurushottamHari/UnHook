"""
Utility for cleaning subtitles.
"""

import json
import re

from data_collector_service.collectors.youtube.models.youtube_video_details import \
    YouTubeVideoDetails
from data_processing_service.models.youtube.subtitle_data import (SubtitleData,
                                                                  SubtitleMap)


class SubtitleUtils:
    """A class for cleaning subtitle files."""

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
        # Join with a space, or '\n' if you want to preserve some structure
        return " ".join(cleaned_lines)

    def _clean_vtt(self, content: str) -> str:
        """Cleans VTT subtitle content."""
        # Remove the WEBVTT header and metadata (up to the first blank line)
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
            # Remove timestamp lines (with possible attributes)
            if re.match(
                r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line
            ):
                continue
            # Remove lines that are just whitespace
            if not line.strip():
                continue
            # Remove tags like <c>, <00:00:00.399>, etc.
            line = re.sub(r"<[^>]+>", "", line)
            # Remove any remaining lines that are just numbers (sequence numbers, rare in VTT)
            if re.match(r"^\d+$", line.strip()):
                continue
            line = line.strip()
            # Remove consecutive duplicates
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
