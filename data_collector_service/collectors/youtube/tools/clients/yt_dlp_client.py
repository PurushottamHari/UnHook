import yt_dlp
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pprint import pprint

logger = logging.getLogger(__name__)

class YtDlpClient:
    """Client for interacting with YouTube using yt-dlp."""
    
    def __init__(self):
        # Base configuration for metadata extraction
        self.metadata_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'socket_timeout': 30,
            'retries': 3,
            'verbose': False,
            'no_warnings': True,
            'playlistreverse': True,  # Get videos in reverse chronological order,
            'noprogress': True,
            'noprint': True,
        }

    def get_channel_videos(self, channel_name: str, max_videos: int) -> List:
        """
        Get the latest videos from a YouTube channel.
        
        Args:
            channel_id: The YouTube channel ID
            max_videos: Maximum number of videos to retrieve
            
        Returns:
            List[Dict]: List of video information
        """
        url = f"https://www.youtube.com/@{channel_name}/videos"
        logger.info(f"Fetching videos from channel: {channel_name} (max: {max_videos})")
        
        # Create a copy of metadata_opts and update playlistend
        metadata_opts = self.metadata_opts.copy()
        metadata_opts['playlistend'] = max_videos
        
        try:
            with yt_dlp.YoutubeDL(metadata_opts) as ydl:
                channel_info = ydl.extract_info(url, download=False)
                
                if not channel_info:
                    logger.error(f"No channel information returned for channel {channel_id}")
                    return []
                    
                videos = channel_info.get('entries', [])
                logger.info(f"Found {len(videos)} videos in scan")
                
                if not videos:
                    return []
                
                return videos
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube-DL download error for channel {channel_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scanning channel {channel_id}: {str(e)}")
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
        video_opts['extract_flat'] = False

        try:
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                video_info = ydl.extract_info(url, download=False)
                if not video_info:
                    logger.error(f"No video information returned for video_id {video_id}")
                    return None
                return video_info
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube-DL download error for video_id {video_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching video {video_id}: {str(e)}")
            return None