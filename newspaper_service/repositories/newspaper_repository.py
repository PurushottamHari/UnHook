"""
Newspaper repository interface.
"""

from abc import ABC, abstractmethod
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
    async def get_newspaper(self, newspaper_id: str) -> Optional[Newspaper]:
        """Get a newspaper by ID."""
        pass

    @abstractmethod
    async def get_newspapers_by_user(self, user_id: str) -> List[Newspaper]:
        """Get all newspapers for a user."""
        pass

    @abstractmethod
    async def update_newspaper(self, newspaper: Newspaper) -> Newspaper:
        """Update a newspaper."""
        pass
