"""
Metrics processor for generate required content service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor


class GenerateRequiredContentMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for generate required content service.

    Tracks:
    - Total content considered
    - Subtitle download success/failure
    - Best subtitle download success
    - Complete failures
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the generate required content metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "subtitle_download_success": 0,
            "best_subtitle_download_success": 0,
            "complete_failures": 0,
            "content_processed": [],
            "subtitle_download_details": {},  # content_id -> subtitle_info
        }

        super().__init__(
            service_name="generate_required_content_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_content_considered(self, count: int = 1) -> None:
        """
        Record content that was considered for processing.

        Args:
            count: Number of content items considered
        """
        self.data["total_considered"] += count

    def record_subtitle_download_success(
        self, content_id: str, subtitle_info: Dict
    ) -> None:
        """
        Record successful subtitle download.

        Args:
            content_id: ID of the content
            subtitle_info: Information about the downloaded subtitle
        """
        self.data["subtitle_download_success"] += 1
        self.data["subtitle_download_details"][content_id] = subtitle_info

        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_best_subtitle_download_success(self, content_id: str) -> None:
        """
        Record successful best subtitle download.

        Args:
            content_id: ID of the content
        """
        self.data["best_subtitle_download_success"] += 1

    def record_complete_failure(self, content_id: str, reason: str) -> None:
        """
        Record complete failure (no subtitle could be downloaded).

        Args:
            content_id: ID of the content
            reason: Reason for failure
        """
        self.data["complete_failures"] += 1
        self.data["subtitle_download_details"][content_id] = {
            "status": "failed",
            "reason": reason,
        }

        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def get_total_considered(self) -> int:
        """
        Get the total number of content items considered.

        Returns:
            Total number of content items considered
        """
        return self.data["total_considered"]

    def get_subtitle_download_success_count(self) -> int:
        """
        Get the number of successful subtitle downloads.

        Returns:
            Number of successful subtitle downloads
        """
        return self.data["subtitle_download_success"]

    def get_best_subtitle_download_success_count(self) -> int:
        """
        Get the number of successful best subtitle downloads.

        Returns:
            Number of successful best subtitle downloads
        """
        return self.data["best_subtitle_download_success"]

    def get_complete_failures_count(self) -> int:
        """
        Get the number of complete failures.

        Returns:
            Number of complete failures
        """
        return self.data["complete_failures"]

    def get_content_processed(self) -> List[str]:
        """
        Get the list of content IDs that were processed.

        Returns:
            List of content IDs that were processed
        """
        return self.data["content_processed"]

    def get_subtitle_download_details(self) -> Dict[str, Dict]:
        """
        Get detailed subtitle download information.

        Returns:
            Dictionary mapping content IDs to subtitle download details
        """
        return self.data["subtitle_download_details"]
