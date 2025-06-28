from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .enums import ContentType

class ContentStatus(str, Enum):
    COLLECTED = "COLLECTED"
    PROCESSING = "PROCESSING"
    USED = "USED"
    REJECTED = "REJECTED"


class ContentSubStatus(str, Enum):
    MODERATION_PASSED = "MODERATION_PASSED"
    SUBTITLES_STORED = "SUBTITLES_STORED"

@dataclass
class SubStatusDetail:
    sub_status: ContentSubStatus
    created_at: datetime
    reason: str = ""

@dataclass
class StatusDetail:
    status: ContentStatus
    created_at: datetime
    reason: str = ""

@dataclass
class UserCollectedContent:
    id: str
    content_type: ContentType
    user_id: str
    external_id: str
    output_type: str
    status: ContentStatus
    status_details: List[StatusDetail]
    data: Dict[str, any]
    sub_status: Optional[ContentSubStatus] = None
    sub_status_details: List[SubStatusDetail] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    

    def add_status_detail(self, status: ContentStatus, reason: str = ""):
        status_detail = StatusDetail(
            status=status,
            created_at=datetime.utcnow(),
            reason=reason
        )
        self.status_details.append(status_detail)
        self.status = status
        self.updated_at = datetime.utcnow() 

    def add_sub_status_detail(self, sub_status: ContentSubStatus, reason: str = ""):
        status_detail = SubStatusDetail(
            sub_status=sub_status,
            created_at=datetime.utcnow(),
            reason=reason
        )
        self.sub_status_details.append(status_detail)
        self.sub_status = sub_status
        self.updated_at = datetime.utcnow()     