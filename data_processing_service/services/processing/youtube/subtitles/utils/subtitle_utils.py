"""
Utility for cleaning subtitles.
"""

import re
import json
import requests
import os

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
        if extension == 'srt':
            return self._clean_srt(subtitle_content)
        elif extension == 'vtt':
            return self._clean_vtt(subtitle_content)
        elif extension == 'json3':
            return self._clean_json3(subtitle_content)
        else:
            # Default fallback for unknown formats
            raise RuntimeError("Subtitle file format unsupported: " + extension)

    def _clean_srt(self, content: str) -> str:
        """Cleans SRT subtitle content."""
        lines = content.splitlines()
        cleaned_lines = []
        for line in lines:
            # Skip sequence numbers (lines that are just digits)
            if re.match(r'^\d+$', line.strip()):
                continue
            # Skip timestamp lines
            if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line.strip()):
                continue
            # Skip empty lines
            if line.strip() == '':
                continue
            cleaned_lines.append(line.strip())
        # Join with a space, or '\n' if you want to preserve some structure
        return ' '.join(cleaned_lines)

    def _clean_vtt(self, content: str) -> str:
        """Cleans VTT subtitle content."""
        # Remove the WEBVTT header and metadata (up to the first blank line)
        if content.startswith("WEBVTT"):
            header_end = content.find('\n\n')
            if header_end != -1:
                content = content[header_end+2:]
            else:
                content = '\n'.join(content.splitlines()[1:])

        lines = content.splitlines()
        cleaned_lines = []
        prev_line = None
        for line in lines:
            # Remove timestamp lines (with possible attributes)
            if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line):
                continue
            # Remove lines that are just whitespace
            if not line.strip():
                continue
            # Remove tags like <c>, <00:00:00.399>, etc.
            line = re.sub(r'<[^>]+>', '', line)
            # Remove any remaining lines that are just numbers (sequence numbers, rare in VTT)
            if re.match(r'^\d+$', line.strip()):
                continue
            line = line.strip()
            # Remove consecutive duplicates
            if line and line != prev_line:
                cleaned_lines.append(line)
            prev_line = line
        return ' '.join(cleaned_lines)

    def _clean_json3(self, content: str) -> str:
        """Cleans json3 subtitle content."""
        try:
            data = json.loads(content)
            text_segments = []
            if 'events' in data:
                for event in data['events']:
                    if 'segs' in event:
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                text_segments.append(seg['utf8'])
            return ''.join(text_segments).replace('\n', ' ').strip()
        except json.JSONDecodeError:
            return ""

    def download_subtitle_file(self, url: str) -> str:
        """
        Downloads the subtitle file from the given URL.

        Args:
            url: The URL of the subtitle file.

        Returns:
            The content of the subtitle file as a string.
        """
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        content = response.text
        if not content or not content.strip():
            raise ValueError("Downloaded subtitle content is empty.")
        return content 
