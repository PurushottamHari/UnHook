from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

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
