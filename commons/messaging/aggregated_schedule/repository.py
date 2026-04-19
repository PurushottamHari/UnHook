from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .models import AggregatedSchedule, AggregatedScheduleStatus


class AggregatedScheduleRepository(ABC):
    """Abstract base class for managing aggregated schedules."""

    @abstractmethod
    async def get_active_schedule(
        self, name: str, aggregation_key: str
    ) -> Optional[AggregatedSchedule]:
        """Retrieve an active (initialized) schedule by name and key."""
        pass

    @abstractmethod
    async def create_schedule(self, schedule: AggregatedSchedule) -> AggregatedSchedule:
        """Create a new aggregated schedule."""
        pass

    @abstractmethod
    async def get_by_id(self, schedule_id: str) -> Optional[AggregatedSchedule]:
        """Retrieve a schedule by its ID."""
        pass

    @abstractmethod
    async def update_schedule(self, schedule: AggregatedSchedule) -> None:
        """Update an existing aggregated schedule."""
        pass
