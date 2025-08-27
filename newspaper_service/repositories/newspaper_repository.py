"""
Newspaper repository interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from data_collector_service.models.user_collected_content import \
    UserCollectedContent

from ..models import Newspaper


class NewspaperRepository(ABC):
    """Abstract interface for newspaper repository operations."""

    @abstractmethod
    def create_newspaper(
        self, newspaper: Newspaper, considered_user_contents: List[UserCollectedContent]
    ) -> Newspaper:
        """Create a new newspaper and update considered user content in one operation."""
        pass

    @abstractmethod
    def get_newspaper(self, newspaper_id: str) -> Optional[Newspaper]:
        """Get a newspaper by ID."""
        pass

    @abstractmethod
    def get_newspaper_by_user_and_date(
        self, user_id: str, for_date: datetime
    ) -> Optional[Newspaper]:
        """Get a newspaper for a specific user and date."""
        pass

    @abstractmethod
    def upsert_newspaper(self, newspaper: Newspaper) -> Newspaper:
        """Create or update newspaper with all its associated content."""
        pass
