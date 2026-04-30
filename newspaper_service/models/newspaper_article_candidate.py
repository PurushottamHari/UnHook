from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class CandidateStatus(str, Enum):
    """Status of an article candidate for a newspaper."""

    CONSIDERED = "CONSIDERED"
    PICKED_FOR_EVALUATION = "PICKED_FOR_EVALUATION"
    USED = "USED"
    FAILED = "FAILED"


class CandidateSource(str, Enum):
    """Source of the candidate."""

    USER_COLLECTED_CONTENT = "USER_COLLECTED_CONTENT"


class CandidateType(str, Enum):
    """Type of the candidate."""

    USER_COLLECTED_CONTENT = "USER_COLLECTED_CONTENT"


@dataclass
class CandidateStatusDetail:
    """Detail information about a status change for a candidate."""

    status: CandidateStatus
    created_at: datetime
    reason: str = ""


@dataclass
class CandidateLinks:
    """Links associated with a candidate."""

    user_collected_content_id: Optional[str] = None
    generated_content_id: Optional[str] = None
    generated_content_id_list: List[str] = field(default_factory=list)


@dataclass
class NewspaperArticleCandidate:
    """An article candidate being considered for a newspaper."""

    id: str
    linked_id: str  # The ID from the source (e.g., user_collected_content_id)
    source: CandidateSource
    type: CandidateType
    user_id: str
    links: CandidateLinks
    newspaper_id: Optional[str] = None
    status: CandidateStatus = CandidateStatus.CONSIDERED
    status_details: List[CandidateStatusDetail] = field(default_factory=list)
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set_status(self, status: CandidateStatus, reason: str = "") -> None:
        """Set candidate status and append to history with timestamp."""
        self.status = status
        self.status_details.append(
            CandidateStatusDetail(
                status=status, created_at=datetime.utcnow(), reason=reason
            )
        )
        self.updated_at = datetime.utcnow()
