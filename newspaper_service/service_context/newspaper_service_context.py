"""
Newspaper service-specific context.
"""

import os
from typing import Optional, Type

from commons.metrics_processor.base_metrics_processor import \
    BaseMetricsProcessor
from commons.service_context import BaseServiceContext


class NewspaperServiceContext(BaseServiceContext):
    """
    Newspaper service-specific context.

    Provides common functionality that newspaper services can use.
    Each service should pass its metrics processor class to the constructor.
    """

    def __init__(
        self, metrics_processor_class: Optional[Type[BaseMetricsProcessor]] = None
    ):
        """
        Initialize the newspaper service context.

        Args:
            metrics_processor_class: The metrics processor class to instantiate
        """
        super().__init__()

        # Auto-initialize metrics processor if class is provided
        if metrics_processor_class:
            self._initialize_metrics_processor(metrics_processor_class)

    def _initialize_metrics_processor(
        self, metrics_processor_class: Type[BaseMetricsProcessor]
    ) -> None:
        """
        Initialize the metrics processor for this service.

        Args:
            metrics_processor_class: The metrics processor class to instantiate
        """
        try:
            # Get pipeline ID from environment
            pipeline_id = os.getenv("PIPELINE_ID")
            if pipeline_id:
                metrics_processor = metrics_processor_class(pipeline_id)
                self.set_metrics_processor(metrics_processor)
                print(
                    f"✅ Newspaper metrics processor initialized for pipeline: {pipeline_id}"
                )
            else:
                print("⚠️  No pipeline ID found - newspaper metrics collection disabled")
        except Exception as e:
            print(f"⚠️  Failed to initialize newspaper metrics processor: {e}")

    def set_metrics_processor(self, metrics_processor: BaseMetricsProcessor) -> None:
        """
        Set the metrics processor for this service.

        Args:
            metrics_processor: The metrics processor to set
        """
        super().set_metrics_processor(metrics_processor)

    def get_metrics_processor(self) -> Optional[BaseMetricsProcessor]:
        """
        Get the current metrics processor.

        Returns:
            The current metrics processor or None if not set
        """
        return super().get_metrics_processor()
