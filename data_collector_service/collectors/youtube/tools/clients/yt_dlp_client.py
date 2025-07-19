import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Optional

import yt_dlp

logger = logging.getLogger(__name__)


class YtDlpClient:
    """Client for interacting with YouTube using yt-dlp."""

    def __init__(self):
        # Base configuration for metadata extraction
        self.metadata_opts = {
            "quiet": True,
            "extract_flat": True,
            "force_generic_extractor": True,
            "socket_timeout": 30,
            "retries": 3,
            "verbose": False,
            "no_warnings": True,
            "playlistreverse": True,  # Get videos in reverse chronological order,
            "noprogress": True,
            "noprint": True,
        }

    def get_channel_videos(self, channel_name: str, max_videos: int) -> List:
        """
        Get the latest videos from a YouTube channel.

        Args:
            channel_name: The YouTube channel name
            max_videos: Maximum number of videos to retrieve

        Returns:
            List[Dict]: List of video information
        """
        url = f"https://www.youtube.com/@{channel_name}/videos"
        logger.info(f"Fetching videos from channel: {channel_name} (max: {max_videos})")

        # Create a copy of metadata_opts and update playlistend
        metadata_opts = self.metadata_opts.copy()
        metadata_opts["playlistend"] = max_videos

        try:
            with yt_dlp.YoutubeDL(metadata_opts) as ydl:
                channel_info = ydl.extract_info(url, download=False)

                if not channel_info:
                    logger.error(
                        f"No channel information returned for channel {channel_name} (URL: {url}). The channel may not exist, may have been renamed, or is unavailable."
                    )
                    return []

                videos = channel_info.get("entries", [])
                logger.info(f"Found {len(videos)} videos in scan")

                if not videos:
                    return []

                return videos

        except yt_dlp.utils.DownloadError as e:
            logger.error(
                f"YouTube-DL download error for channel {channel_name} (URL: {url}): {str(e)}. The channel may have been renamed, deleted, or is unavailable."
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error scanning channel {channel_name} (URL: {url}): {str(e)}"
            )
            return []

    def get_video_data(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific YouTube video by its video ID.

        Args:
            video_id: The YouTube video ID
        Returns:
            Dict: Video information dictionary, or None if not found/error
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"Fetching video data for video_id: {video_id}")

        # Use a copy of metadata_opts but ensure extract_flat is False for full video info
        video_opts = self.metadata_opts.copy()
        video_opts["extract_flat"] = False

        try:
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                video_info = ydl.extract_info(url, download=False)
                if not video_info:
                    logger.error(
                        f"No video information returned for video_id {video_id}"
                    )
                    return None
                return video_info
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube-DL download error for video_id {video_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching video {video_id}: {str(e)}")
            return None

    def download_subtitles(
        self, video_id: str, language: str, fmt: str, subtitle_type: str
    ):
        """
        Download subtitles for a given YouTube video using yt-dlp client, return as string and delete the file.
        Args:
            video_url (str): The URL of the YouTube video.
            output_dir (Path or str): Directory to save the subtitles.
            languages (list or None): List of language codes (e.g., ['en', 'hi']). Defaults to ['en', 'hi'].
            fmt (str): Subtitle file format (e.g., 'json3', 'vtt'). Defaults to 'srt'.
            output_filename (str or None): Ignored in this version.
        Returns:
            str or None: Subtitle content as string, or None if failed.
        """
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_dir = Path(f"subtitles/{language}/{fmt}")
        output_dir.mkdir(parents=True, exist_ok=True)
        # Set subtitle options based on subtitle_type
        if subtitle_type == "automatic":
            writesubtitles = False
            writeautomaticsub = True
        elif subtitle_type == "manual":
            writesubtitles = True
            writeautomaticsub = False
        else:
            writesubtitles = True
            writeautomaticsub = True
        subtitle_opts = {
            "writesubtitles": writesubtitles,
            "writeautomaticsub": writeautomaticsub,
            "subtitleslangs": [language],
            "subtitlesformat": fmt,
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "paths": {"subtitle": str(output_dir)},
        }
        try:
            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                ydl.download([video_url])
                import random
                import time

                time.sleep(random.uniform(8, 12))

            video_id = None
            m = re.search(r"v=([\w-]+)", video_url)
            if m:
                video_id = m.group(1)

            pattern = re.compile(rf".*\[{video_id}\]\.{language}\.{fmt}$")
            for file in os.listdir(output_dir):
                if pattern.match(file):
                    src = output_dir / file
                    try:
                        with open(src, "r", encoding="utf-8") as f:
                            content = f.read()
                        src.unlink()  # Delete the file after reading
                        return content
                    except Exception as e:
                        logger.error(
                            f"Error reading/deleting subtitle file {src}: {str(e)}"
                        )
                        return None
            logger.error(
                f"No matching subtitle file found for {video_url} in {output_dir}"
            )
            return None
        except Exception as e:
            logger.error(f"✗ Error downloading subtitles for {video_url}: {str(e)}")
            return None
