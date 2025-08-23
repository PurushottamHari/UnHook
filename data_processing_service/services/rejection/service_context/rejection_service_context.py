"""
Rejection service-specific context.
"""

import os
from typing import Optional

from commons.service_context import BaseServiceContext

from ..metrics_processor.rejection_metrics_processor import \
    RejectionMetricsProcessor


class RejectionServiceContext(BaseServiceContext):
    """
    Rejection service-specific context.

    Extends the base service context with rejection-specific functionality
    and auto-initializes the appropriate metrics processor.
    """

    def __init__(self):
        """Initialize the rejection service context."""
        super().__init__()
        self._initialize_metrics_processor()

    def _initialize_metrics_processor(self) -> None:
        """Initialize the metrics processor for this service."""
        try:
            # Get pipeline ID from environment
            pipeline_id = os.getenv("PIPELINE_ID")
            if pipeline_id:
                metrics_processor = RejectionMetricsProcessor(pipeline_id)
                self.set_metrics_processor(metrics_processor)
                print(
                    f"✅ Rejection metrics processor initialized for pipeline: {pipeline_id}"
                )
            else:
                print("⚠️  No pipeline ID found - rejection metrics collection disabled")
        except Exception as e:
            print(f"⚠️  Failed to initialize rejection metrics processor: {e}")

    def get_rejection_metrics_processor(self) -> Optional[RejectionMetricsProcessor]:
        """
        Get the rejection metrics processor with proper typing.

        Returns:
            The rejection metrics processor or None if not set
        """
        metrics_processor = self.get_metrics_processor()
        if isinstance(metrics_processor, RejectionMetricsProcessor):
            return metrics_processor
        return None
