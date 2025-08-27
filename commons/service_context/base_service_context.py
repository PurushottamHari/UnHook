"""
Base service context for dependency injection across services.
"""

import contextvars
from typing import Any, Optional

from ..metrics_processor.base_metrics_processor import BaseMetricsProcessor


class BaseServiceContext:
    """
    Base service context manager for dependency injection.

    Provides common functionality that service-specific contexts can extend.
    Each service should create its own context class that inherits from this.
    """

    def __init__(self):
        """Initialize the base service context."""
        self._context_vars = {}

    def set_dependency(self, name: str, dependency: Any) -> None:
        """
        Set a dependency in the current context.

        Args:
            name: Name of the dependency
            dependency: The dependency object to set
        """
        if name not in self._context_vars:
            self._context_vars[name] = contextvars.ContextVar(
                f"service_{name}", default=None
            )
        self._context_vars[name].set(dependency)

    def get_dependency(self, name: str) -> Optional[Any]:
        """
        Get a dependency from the current context.

        Args:
            name: Name of the dependency

        Returns:
            The dependency or None if not set
        """
        if name not in self._context_vars:
            return None
        return self._context_vars[name].get()

    def clear_dependency(self, name: str) -> None:
        """
        Clear a dependency from the current context.

        Args:
            name: Name of the dependency to clear
        """
        if name in self._context_vars:
            try:
                self._context_vars[name].reset(self._context_vars[name].get())
            except LookupError:
                pass  # No value set, nothing to clear

    def with_dependency(self, name: str, dependency: Any):
        """
        Context manager to temporarily set a dependency.

        Args:
            name: Name of the dependency
            dependency: The dependency to use in this context

        Returns:
            Context manager that sets and clears the dependency
        """
        return _ServiceContextManager(self, name, dependency)

    def get_metrics_processor(self) -> Optional[BaseMetricsProcessor]:
        """
        Get the current metrics processor from context.

        Returns:
            The current metrics processor or None if not set
        """
        return self.get_dependency("metrics_processor")

    def set_metrics_processor(self, metrics_processor: BaseMetricsProcessor) -> None:
        """
        Set the metrics processor in the current context.

        Args:
            metrics_processor: The metrics processor to set
        """
        self.set_dependency("metrics_processor", metrics_processor)


class _ServiceContextManager:
    """Internal context manager for temporary dependency injection."""

    def __init__(self, service_context: BaseServiceContext, name: str, dependency: Any):
        self.service_context = service_context
        self.name = name
        self.dependency = dependency
        self._token = None

    def __enter__(self):
        """Set the dependency in context."""
        if self.name not in self.service_context._context_vars:
            self.service_context._context_vars[self.name] = contextvars.ContextVar(
                f"service_{self.name}", default=None
            )
        self._token = self.service_context._context_vars[self.name].set(self.dependency)
        return self.dependency

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset the context to its previous state."""
        if self._token:
            self.service_context._context_vars[self.name].reset(self._token)
