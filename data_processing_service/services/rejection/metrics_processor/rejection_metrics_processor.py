"""
Metrics processor for rejection service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import BaseMetricsProcessor


class RejectionMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for rejection service.

    Tracks:
    - Total content considered
    - Content rejected by channel
    - Success/failure rates
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the rejection metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "total_rejected": 0,
            "rejected_by_channel": {},  # channel_name -> count
            "channels_processed": [],
            "success_rate": 0.0,
        }

        super().__init__(
            service_name="rejection_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_content_considered(self, count: int = 1) -> None:
        """
        Record content that was considered for rejection.

        Args:
            count: Number of content items considered
        """
        self.data["total_considered"] += count

    def record_content_rejected(self, channel_name: str, count: int = 1) -> None:
        """
        Record content that was rejected.

        Args:
            channel_name: Name of the channel
            count: Number of content items rejected
        """
        self.data["total_rejected"] += count

        if channel_name not in self.data["rejected_by_channel"]:
            self.data["rejected_by_channel"][channel_name] = 0
        self.data["rejected_by_channel"][channel_name] += count

    def record_channel_processed(self, channel_name: str) -> None:
        """
        Record that a channel was processed.

        Args:
            channel_name: Name of the channel that was processed
        """
        if channel_name not in self.data["channels_processed"]:
            self.data["channels_processed"].append(channel_name)

    def calculate_success_rate(self) -> None:
        """Calculate the success rate (content not rejected)."""
        if self.data["total_considered"] > 0:
            accepted = self.data["total_considered"] - self.data["total_rejected"]
            self.data["success_rate"] = (accepted / self.data["total_considered"]) * 100

    def get_total_considered(self) -> int:
        """
        Get the total number of content items considered.

        Returns:
            Total number of content items considered
        """
        return self.data["total_considered"]

    def get_total_rejected(self) -> int:
        """
        Get the total number of content items rejected.

        Returns:
            Total number of content items rejected
        """
        return self.data["total_rejected"]

    def get_rejected_by_channel(self) -> Dict[str, int]:
        """
        Get the rejection count by channel.

        Returns:
            Dictionary mapping channel names to rejection counts
        """
        return self.data["rejected_by_channel"]

    def get_channels_processed(self) -> List[str]:
        """
        Get the list of channels that were processed.

        Returns:
            List of channel names that were processed
        """
        return self.data["channels_processed"]

    def get_success_rate(self) -> float:
        """
        Get the success rate percentage.

        Returns:
            Success rate as a percentage
        """
        return self.data["success_rate"]
