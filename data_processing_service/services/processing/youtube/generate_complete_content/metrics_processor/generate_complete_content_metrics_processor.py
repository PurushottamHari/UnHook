"""
Metrics processor for generate complete content service.
"""

import time
from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor


class GenerateCompleteContentMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for generate complete content service.

    Tracks:
    - Total content considered
    - Content successfully generated
    - Generation failures
    - Average creation time
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the generate complete content metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "successfully_generated": 0,
            "generation_failures": 0,
            "content_processed": [],
            "failure_details": {},  # content_id -> failure_reason
            "generation_times": [],  # List of generation times in seconds
            "total_generation_time": 0.0,
        }

        super().__init__(
            service_name="generate_complete_content_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_content_considered(self, count: int = 1) -> None:
        """
        Record content that was considered for generation.

        Args:
            count: Number of content items considered
        """
        self.data["total_considered"] += count

    def record_successful_generation(
        self, content_id: str, generation_time: float
    ) -> None:
        """
        Record successful content generation.

        Args:
            content_id: ID of the content that was successfully generated
            generation_time: Time taken for generation in seconds
        """
        self.data["successfully_generated"] += 1
        self.data["generation_times"].append(generation_time)
        self.data["total_generation_time"] += generation_time
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_generation_failure(self, content_id: str, reason: str) -> None:
        """
        Record generation failure.

        Args:
            content_id: ID of the content that failed generation
            reason: Reason for the failure
        """
        self.data["generation_failures"] += 1
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

    def get_successfully_generated_count(self) -> int:
        """
        Get the number of successfully generated items.

        Returns:
            Number of successfully generated items
        """
        return self.data["successfully_generated"]

    def get_generation_failures_count(self) -> int:
        """
        Get the number of generation failures.

        Returns:
            Number of generation failures
        """
        return self.data["generation_failures"]

    def get_average_generation_time(self) -> float:
        """
        Get the average generation time in seconds.

        Returns:
            Average generation time in seconds, or 0.0 if no successful generations
        """
        if self.data["successfully_generated"] > 0:
            return (
                self.data["total_generation_time"] / self.data["successfully_generated"]
            )
        return 0.0

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
