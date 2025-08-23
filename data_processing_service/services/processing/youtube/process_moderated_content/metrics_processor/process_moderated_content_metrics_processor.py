"""
Metrics processor for process moderated content service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor


class ProcessModeratedContentMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for process moderated content service.

    Tracks:
    - Total content considered
    - Content successfully processed
    - Processing failures
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the process moderated content metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "successfully_processed": 0,
            "processing_failures": 0,
            "content_processed": [],
            "failure_details": {},  # content_id -> failure_reason
        }

        super().__init__(
            service_name="process_moderated_content_service",
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

    def record_successful_processing(self, content_id: str) -> None:
        """
        Record successful content processing.

        Args:
            content_id: ID of the content that was successfully processed
        """
        self.data["successfully_processed"] += 1
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_processing_failure(self, content_id: str, reason: str) -> None:
        """
        Record processing failure.

        Args:
            content_id: ID of the content that failed processing
            reason: Reason for the failure
        """
        self.data["processing_failures"] += 1
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

    def get_successfully_processed_count(self) -> int:
        """
        Get the number of successfully processed items.

        Returns:
            Number of successfully processed items
        """
        return self.data["successfully_processed"]

    def get_processing_failures_count(self) -> int:
        """
        Get the number of processing failures.

        Returns:
            Number of processing failures
        """
        return self.data["processing_failures"]

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
