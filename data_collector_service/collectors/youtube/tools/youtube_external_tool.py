from datetime import datetime

from data_collector_service.collectors.youtube.models.youtube_video_details import \
    YouTubeVideoDetails
from data_collector_service.collectors.youtube.tools.adapters.youtube_video_adapter import \
    YouTubeVideoAdapter
from data_collector_service.collectors.youtube.tools.clients.yt_dlp_client import \
    YtDlpClient


class YouTubeExternalTool:
    """External tool for interacting with YouTube API."""

    def __init__(self):
        self.yt_dlp_client = YtDlpClient()

    def find_latest_videos(
        self, channel_name: str, max: int
    ) -> list[YouTubeVideoDetails]:
        """
        Find the latest videos from YouTube.

        Args:
            channel_name: Name of the YouTube channel
            max: Maximum number of videos to retrieve

        Returns:
            list: List of YouTubeVideoDetails objects
        """
        videos_data = self.yt_dlp_client.get_channel_videos(
            channel_name=channel_name, max_videos=max
        )
        filtered_videos_data = [v for v in videos_data if not v.get("live_status")]
        return YouTubeVideoAdapter.to_video_details_list(
            filtered_videos_data, channel_name
        )

    def enrich_video_data_with_details(
        self, youtube_video_details: list[YouTubeVideoDetails]
    ):
        enriched_video_list = []
        for youtube_video_detail in youtube_video_details:
            video_details_dict = self.yt_dlp_client.get_video_data(
                video_id=youtube_video_detail.video_id
            )
            if video_details_dict:
                data = YouTubeVideoAdapter.enrich_video_detail(
                    youtube_video_detail, video_details_dict
                )
                if data:
                    enriched_video_list.append(data)

        return enriched_video_list

    def download_subtitles(
        self,
        video_id: str,
        language: str,
        fmt: str,
        subtitle_type: str,
        use_proxy: bool = True,
    ) -> str:
        return self.yt_dlp_client.download_subtitles(
            video_id, language, fmt, subtitle_type, use_proxy
        )
