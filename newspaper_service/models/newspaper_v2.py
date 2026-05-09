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


@dataclass
class NewspaperV2:
    """Simplified newspaper model for the new collation flow with optimistic locking."""

    id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: NewspaperStatus = NewspaperStatus.COLLATING
    status_details: List[StatusDetail] = field(default_factory=list)
    reading_time_in_seconds: int = 0
    version: int = 1

    def set_status(self, status: NewspaperStatus, reason: str = "") -> None:
        """Set status and append to status_details with timestamp."""
        self.status = status
        self.status_details.append(
            StatusDetail(status=status, created_at=datetime.utcnow(), reason=reason)
        )
        self.updated_at = datetime.utcnow()
