"""
Repository interface for accessing user_collected_content collection.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from data_collector_service.models.user_collected_content import (
    ContentStatus, UserCollectedContent)
from user_service.models.enums import CategoryName


class UserCollectedContentRepository(ABC):
    @abstractmethod
    def get_content_with_status(
        self,
        user_id: str,
        status: ContentStatus,
        before_time: Optional[datetime] = None,
    ) -> List[UserCollectedContent]:
        """Return list of UserCollectedContent for the given status and optional cutoff time."""
        pass

    @abstractmethod
    def bulk_update_user_collected_content(
        self, contents: List[UserCollectedContent], session: Any = None
    ) -> int:
        """Persist provided user collected contents via one atomic bulk operation. Returns modified count."""
        pass

    @abstractmethod
    def get_content_by_id(self, content_id: str) -> Optional[UserCollectedContent]:
        """Get a single user collected content by ID."""
        pass
