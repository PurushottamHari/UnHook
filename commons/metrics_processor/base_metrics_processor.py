"""
Base metrics processor for tracking service performance and data collection.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


class BaseMetricsProcessor:
    """
    Base class for metrics processing across services.

    Handles:
    - Service identification and pipeline context
    - Data accumulation throughout service execution
    - Automatic persistence to file-based storage
    - Failure detection if complete() is not called
    """

    def __init__(
        self, service_name: str, pipeline_id: str, data_structure: Dict[str, Any]
    ):
        """
        Initialize the metrics processor.

        Args:
            service_name: Name of the service (e.g., 'data_collector_service')
            pipeline_id: Unique identifier for the pipeline run
            data_structure: Initial data structure for metrics collection
        """
        self.service_name = service_name
        self.pipeline_id = pipeline_id
        self.data = data_structure.copy()
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.success = True
        self.error_message: Optional[str] = None
        self._completed = False

        # Register cleanup handler for auto-detection of failed runs
        import atexit

        atexit.register(self._cleanup_handler)

    def _cleanup_handler(self):
        """Auto-detect if complete() was not called and mark as failed."""
        if not self._completed:
            self.success = False
            self.error_message = "Service terminated without calling complete()"
            self._save_metrics()

    def _get_metrics_directory(self) -> Path:
        """Get the metrics directory for the current date."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        metrics_dir = Path("metrics_data") / today
        metrics_dir.mkdir(parents=True, exist_ok=True)
        return metrics_dir

    def _save_metrics(self) -> None:
        """Save metrics to file."""
        if not self.end_time:
            self.end_time = datetime.utcnow()

        duration_seconds = (self.end_time - self.start_time).total_seconds()

        metrics_data = {
            "service_name": self.service_name,
            "pipeline_id": self.pipeline_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "data": self.data,
        }

        metrics_dir = self._get_metrics_directory()
        filename = f"pipeline_{self.pipeline_id}.json"
        filepath = metrics_dir / filename

        # Load existing data if file exists
        existing_data = {}
        if filepath.exists():
            try:
                with open(filepath, "r") as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Update with current service metrics
        if "services" not in existing_data:
            existing_data["services"] = {}

        existing_data["services"][self.service_name] = metrics_data

        # Add pipeline-level metadata if not present
        if "pipeline_id" not in existing_data:
            existing_data["pipeline_id"] = self.pipeline_id
            existing_data["created_at"] = datetime.utcnow().isoformat()

        # Save the updated data
        with open(filepath, "w") as f:
            json.dump(existing_data, f, indent=2, default=str)

    def complete(
        self, success: bool = True, error_message: Optional[str] = None
    ) -> None:
        """
        Complete the metrics collection and persist to file.

        Args:
            success: Whether the service completed successfully
            error_message: Error message if the service failed
        """
        self.end_time = datetime.utcnow()
        self.success = success
        self.error_message = error_message
        self._completed = True

        # Unregister cleanup handler since we're completing normally
        import atexit

        try:
            atexit.unregister(self._cleanup_handler)
        except ValueError:
            pass  # Handler might not be registered

        self._save_metrics()

    def update_data(self, key: str, value: Any) -> None:
        """
        Update a specific key in the data structure.

        Args:
            key: Key to update
            value: New value
        """
        self.data[key] = value

    def append_to_list(self, key: str, value: Any) -> None:
        """
        Append a value to a list in the data structure.

        Args:
            key: Key of the list to append to
            value: Value to append
        """
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)

    def increment_counter(self, key: str, increment: int = 1) -> None:
        """
        Increment a counter in the data structure.

        Args:
            key: Key of the counter to increment
            increment: Amount to increment by (default: 1)
        """
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += increment
