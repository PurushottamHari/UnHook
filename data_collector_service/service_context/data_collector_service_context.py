"""
Data collector service-specific context.
"""

import os
from typing import Optional

from commons.service_context import BaseServiceContext

from ..metrics_processor.data_collector_metrics_processor import \
    DataCollectorMetricsProcessor


class DataCollectorServiceContext(BaseServiceContext):
    """
    Data collector service-specific context.

    Extends the base service context with data collector-specific functionality
    and auto-initializes the appropriate metrics processor.
    """

    def __init__(self):
        """Initialize the data collector service context."""
        super().__init__()
        self._initialize_metrics_processor()

    def _initialize_metrics_processor(self) -> None:
        """Initialize the metrics processor for this service."""
        try:
            # Get pipeline ID from environment
            pipeline_id = os.getenv("PIPELINE_ID")
            if pipeline_id:
                metrics_processor = DataCollectorMetricsProcessor(pipeline_id)
                self.set_metrics_processor(metrics_processor)
                print(
                    f"✅ Data collector metrics processor initialized for pipeline: {pipeline_id}"
                )
            else:
                print(
                    "⚠️  No pipeline ID found - data collector metrics collection disabled"
                )
        except Exception as e:
            print(f"⚠️  Failed to initialize data collector metrics processor: {e}")

    def get_data_collector_metrics_processor(
        self,
    ) -> Optional[DataCollectorMetricsProcessor]:
        """
        Get the data collector metrics processor with proper typing.

        Returns:
            The data collector metrics processor or None if not set
        """
        metrics_processor = self.get_metrics_processor()
        if isinstance(metrics_processor, DataCollectorMetricsProcessor):
            return metrics_processor
        return None
