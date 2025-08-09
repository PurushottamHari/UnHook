from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class NewspaperStatus(str, Enum):
    """Status of a newspaper throughout its lifecycle."""

    COLLATING = "COLLATING"
    COLLATION_COMPLETE = "COLLATION_COMPLETE"
    CURATED = "CURATED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


@dataclass
class StatusDetail:
    """Detail information about a status change for a newspaper."""

    status: NewspaperStatus
    created_at: datetime
    reason: str = ""


class ConsideredContentStatus(str, Enum):
    """Status for considered content items."""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass
class ConsideredContentStatusDetail:
    """Detail for a considered content status change."""

    status: ConsideredContentStatus
    created_at: datetime
    reason: str = ""


@dataclass
class ConsideredContent:
    """An item of user-collected content considered for inclusion."""

    user_collected_content_id: str
    considered_content_status: ConsideredContentStatus
    status_details: List[ConsideredContentStatusDetail] = field(default_factory=list)

    def set_status(self, status: ConsideredContentStatus, reason: str = "") -> None:
        """Set considered content status and append to history with timestamp."""
        self.considered_content_status = status
        self.status_details.append(
            ConsideredContentStatusDetail(
                status=status, created_at=datetime.utcnow(), reason=reason
            )
        )


@dataclass
class Newspaper:
    """Curated newspaper for a user with considered and final content lists."""

    id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: NewspaperStatus = NewspaperStatus.COLLATING
    status_details: List[StatusDetail] = field(default_factory=list)
    considered_content_list: List[ConsideredContent] = field(default_factory=list)
    final_content_list: List[str] = field(
        default_factory=list
    )  # user_collected_content_id
    reading_time_in_seconds: int = 0

    def set_status(self, status: NewspaperStatus, reason: str = "") -> None:
        """Set status and append to status_details with timestamp."""
        self.status = status
        self.status_details.append(
            StatusDetail(status=status, created_at=datetime.utcnow(), reason=reason)
        )
        self.updated_at = datetime.utcnow()

    def add_considered_content(self, item: ConsideredContent) -> None:
        """Add an item to the considered content list."""
        self.considered_content_list.append(item)
        self.updated_at = datetime.utcnow()

    def add_final_content_id(self, user_collected_content_id: str) -> None:
        """Add a content id to the final content list."""
        self.final_content_list.append(user_collected_content_id)
        self.updated_at = datetime.utcnow()
