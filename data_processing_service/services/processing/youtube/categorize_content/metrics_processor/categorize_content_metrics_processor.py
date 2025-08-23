"""
Metrics processor for categorize content service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor


class CategorizeContentMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for categorize content service.

    Tracks:
    - Total content considered
    - Content successfully categorized
    - Categorization failures
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the categorize content metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "successfully_categorized": 0,
            "categorization_failures": 0,
            "content_processed": [],
            "failure_details": {},  # content_id -> failure_reason
        }

        super().__init__(
            service_name="categorize_content_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_content_considered(self, count: int = 1) -> None:
        """
        Record content that was considered for categorization.

        Args:
            count: Number of content items considered
        """
        self.data["total_considered"] += count

    def record_successful_categorization(self, content_id: str) -> None:
        """
        Record successful categorization.

        Args:
            content_id: ID of the content that was successfully categorized
        """
        self.data["successfully_categorized"] += 1
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_categorization_failure(self, content_id: str, reason: str) -> None:
        """
        Record categorization failure.

        Args:
            content_id: ID of the content that failed categorization
            reason: Reason for the failure
        """
        self.data["categorization_failures"] += 1
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

    def get_successfully_categorized_count(self) -> int:
        """
        Get the number of successfully categorized items.

        Returns:
            Number of successfully categorized items
        """
        return self.data["successfully_categorized"]

    def get_categorization_failures_count(self) -> int:
        """
        Get the number of categorization failures.

        Returns:
            Number of categorization failures
        """
        return self.data["categorization_failures"]

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
