from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..models import NewspaperV2


class NewspaperV2Repository(ABC):
    """Abstract interface for NewspaperV2 repository operations."""

    @abstractmethod
    def upsert(self, newspaper: NewspaperV2) -> NewspaperV2:
        """Upsert a NewspaperV2 instance."""
        pass

    @abstractmethod
    def get_by_id(self, newspaper_id: str) -> Optional[NewspaperV2]:
        """Get a single NewspaperV2 instance by ID."""
        pass

    @abstractmethod
    def get_by_user_and_date(
        self, user_id: str, for_date: datetime
    ) -> Optional[NewspaperV2]:
        """Get a NewspaperV2 instance for a specific user and date."""
        pass

    @abstractmethod
    def list_by_user_and_date_range(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[NewspaperV2]:
        """List NewspaperV2 instances for a specific user within a date range."""
        pass
