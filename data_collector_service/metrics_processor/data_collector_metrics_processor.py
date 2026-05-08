"""
Metrics processor for data collector service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor


class DataCollectorMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for data collector service.

    Tracks:
    - Videos collected per channel (channel_name -> list of video_ids)
    - Total videos collected
    - Channels processed
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the data collector metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "videos_by_channel": {},  # channel_name -> list of video_ids
            "total_videos": 0,
            "channels_processed": [],
            "channels_with_videos": 0,
        }

        super().__init__(
            service_name="data_collector_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_video_collected(self, channel_name: str, video_id: str) -> None:
        """
        Record a video collected for a specific channel.

        Args:
            channel_name: Name of the channel
            video_id: ID of the collected video
        """
        if channel_name not in self.data["videos_by_channel"]:
            self.data["videos_by_channel"][channel_name] = []
            self.data["channels_with_videos"] += 1

        self.data["videos_by_channel"][channel_name].append(video_id)
        self.data["total_videos"] += 1

    def record_channel_processed(self, channel_name: str) -> None:
        """
        Record that a channel was processed (regardless of whether videos were found).

        Args:
            channel_name: Name of the channel that was processed
        """
        if channel_name not in self.data["channels_processed"]:
            self.data["channels_processed"].append(channel_name)

    def get_channel_video_count(self, channel_name: str) -> int:
        """
        Get the number of videos collected for a specific channel.

        Args:
            channel_name: Name of the channel

        Returns:
            Number of videos collected for the channel
        """
        return len(self.data["videos_by_channel"].get(channel_name, []))

    def get_total_videos(self) -> int:
        """
        Get the total number of videos collected.

        Returns:
            Total number of videos collected
        """
        return self.data["total_videos"]

    def get_channels_processed(self) -> List[str]:
        """
        Get the list of channels that were processed.

        Returns:
            List of channel names that were processed
        """
        return self.data["channels_processed"]

    def get_channels_with_videos(self) -> int:
        """
        Get the number of channels that had videos collected.

        Returns:
            Number of channels with videos collected
        """
        return self.data["channels_with_videos"]
