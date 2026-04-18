"""
Metrics processor for newspaper service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor


class NewspaperMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for newspaper service.

    Tracks:
    - Total content considered
    - Content successfully added to newspaper
    - Newspaper creation failures
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the newspaper metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "content_added_to_newspaper": 0,
            "newspaper_creation_failures": 0,
            "content_processed": [],
            "failure_details": {},  # content_id -> failure_reason
        }

        super().__init__(
            service_name="newspaper_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_content_considered(self, count: int = 1) -> None:
        """
        Record content that was considered for newspaper.

        Args:
            count: Number of content items considered
        """
        self.data["total_considered"] += count

    def record_content_added_to_newspaper(self, content_id: str) -> None:
        """
        Record content successfully added to newspaper.

        Args:
            content_id: ID of the content that was added to newspaper
        """
        self.data["content_added_to_newspaper"] += 1
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_newspaper_creation_failure(self, content_id: str, reason: str) -> None:
        """
        Record newspaper creation failure.

        Args:
            content_id: ID of the content that failed to be added to newspaper
            reason: Reason for the failure
        """
        self.data["newspaper_creation_failures"] += 1
        self.data["failure_details"][content_id] = reason
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def get_total_considered(self) -> int:
        """
        Get the total number of content items considered.

        Returns:
            Total number of content items considered
        """
        return self.data["total_considered"]

    def get_content_added_to_newspaper_count(self) -> int:
        """
        Get the number of content items added to newspaper.

        Returns:
            Number of content items added to newspaper
        """
        return self.data["content_added_to_newspaper"]

    def get_newspaper_creation_failures_count(self) -> int:
        """
        Get the number of newspaper creation failures.

        Returns:
            Number of newspaper creation failures
        """
        return self.data["newspaper_creation_failures"]

    def get_content_processed(self) -> List[str]:
        """
        Get the list of content IDs that were processed.

        Returns:
            List of content IDs that were processed
        """
        return self.data["content_processed"]

    def get_failure_details(self) -> Dict[str, str]:
        """
        Get detailed failure information.

        Returns:
            Dictionary mapping content IDs to failure reasons
        """
        return self.data["failure_details"]
