import copy
import logging
from datetime import datetime
from typing import Dict, List

from data_collector_service.collectors.youtube.models.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_collector_service.collectors.youtube.tools.adapters.subtitle_adapter import (
    SubtitleAdapter,
)
from data_collector_service.collectors.youtube.tools.exceptions.youtube_video_key_data_missing import (
    youtube_video_key_data_missing,
)

logger = logging.getLogger(__name__)


class YouTubeVideoAdapter:
    """Adapter to convert yt-dlp video data to YouTubeVideoDetails objects."""

    @staticmethod
    def to_video_details(video_data: Dict, channel_name: str) -> YouTubeVideoDetails:
        """
        Convert a single video data dictionary to YouTubeVideoDetails object.

        Args:
            video_data: Dictionary containing video information from yt-dlp
            channel_name: Name of the YouTube channel

        Returns:
            YouTubeVideoDetails: Converted video details object
        Raises:
            youtube_video_key_data_missing: If 'id' or 'title' is missing or empty
        """
        # Validate required fields
        if not video_data.get("id") or not video_data.get("title"):
            raise youtube_video_key_data_missing(
                "'id' and 'title' are required fields and must not be empty."
            )

        # Get the highest quality thumbnail URL
        thumbnails = video_data.get("thumbnails", [])
        thumbnail_url = ""
        if thumbnails:
            # Get the highest resolution thumbnail
            highest_res = max(
                thumbnails, key=lambda x: x.get("width", 0) * x.get("height", 0)
            )
            thumbnail_url = highest_res.get("url", "")

        # Handle release date - only set if timestamp is present
        release_date = None
        if video_data.get("timestamp"):
            release_date = datetime.fromtimestamp(video_data["timestamp"])

        return YouTubeVideoDetails(
            video_id=video_data.get("id"),
            title=video_data.get("title"),
            channel_id=video_data.get("channel_id"),
            channel_name=channel_name,
            description=video_data.get("description", ""),
            release_date=release_date,
            views=video_data.get("view_count", 0),
            thumbnail=thumbnail_url,
        )

    @staticmethod
    def to_video_details_list(
        videos_data: List[Dict], channel_name: str
    ) -> List[YouTubeVideoDetails]:
        """
        Convert a list of video data dictionaries to YouTubeVideoDetails objects.

        Args:
            videos_data: List of dictionaries containing video information from yt-dlp
            channel_name: Name of the YouTube channel

        Returns:
            List[YouTubeVideoDetails]: List of converted video details objects
        """
        result = []
        for video in videos_data:
            try:
                result.append(YouTubeVideoAdapter.to_video_details(video, channel_name))
            except youtube_video_key_data_missing as e:
                logger.error(
                    f"Missing key data for video in channel {channel_name}: {str(e)}"
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error processing video in channel {channel_name}: {str(e)}"
                )
        return result

    @staticmethod
    def enrich_video_detail(
        old_youtube_video_details: YouTubeVideoDetails, enrich_details_dict: Dict
    ) -> YouTubeVideoDetails:
        """
        Add more details into the object such as tags, language, release_date
        """
        release_epoch = None
        if enrich_details_dict.get("timestamp"):
            release_epoch = enrich_details_dict["timestamp"]

        if not release_epoch and enrich_details_dict.get("timestamp"):
            release_epoch = enrich_details_dict["timestamp"]
        if not release_epoch:
            raise youtube_video_key_data_missing(
                "'timestamp/release_timestamp' is a required field for enrichment: "
                + old_youtube_video_details.video_id
            )
        subtitles = SubtitleAdapter.from_enrich_dict(enrich_details_dict)
        if not subtitles:
            logger.warn(
                "Subtitles not found for: " + old_youtube_video_details.video_id
            )
            return None
        subtitles.validate_not_empty()

        # Create a new clone from the old object
        new_video_details = copy.deepcopy(old_youtube_video_details)

        # Enrich with new details from the dictionary
        new_video_details.tags = enrich_details_dict.get("tags", new_video_details.tags)
        new_video_details.categories = enrich_details_dict.get(
            "categories", new_video_details.categories
        )
        new_video_details.language = enrich_details_dict.get(
            "language", new_video_details.language
        )
        new_video_details.release_date = datetime.fromtimestamp(release_epoch)
        new_video_details.title = enrich_details_dict.get(
            "title", new_video_details.title
        )
        new_video_details.description = enrich_details_dict.get(
            "description", new_video_details.description
        )
        new_video_details.views = enrich_details_dict.get(
            "view_count", new_video_details.views
        )
        new_video_details.likes_count = enrich_details_dict.get(
            "like_count", new_video_details.likes_count
        )
        new_video_details.comments_count = enrich_details_dict.get(
            "comment_count", new_video_details.comments_count
        )
        new_video_details.duration_in_seconds = enrich_details_dict.get(
            "duration", new_video_details.duration_in_seconds
        )
        new_video_details.subtitles = subtitles
        return new_video_details
