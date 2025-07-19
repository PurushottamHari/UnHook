"""
Model for generated content.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from data_collector_service.models import ContentType
from user_service.models import CategoryName, OutputType


class GeneratedContentStatus(str, Enum):
    REQUIRED_CONTENT_GENERATED = "REQUIRED_CONTENT_GENERATED"
    CATEGORIZATION_COMPLETED = "CATEGORIZATION_COMPLETED"


@dataclass
class StatusDetail:
    status: GeneratedContentStatus
    created_at: datetime
    reason: str = ""


@dataclass
class GeneratedData:
    markdown_string: str = ""
    string: str = ""


@dataclass
class CategoryInfo:
    category: CategoryName
    category_description: str = ""
    category_tags: List[str] = field(default_factory=list)


@dataclass
class GeneratedContent:
    """Model representing generated content from collected content."""

    id: str
    external_id: str
    content_type: ContentType
    status: GeneratedContentStatus
    status_details: StatusDetail
    content_generated_at: datetime
    category: Optional[CategoryInfo] = None
    generated: Dict[str, GeneratedData] = field(default_factory=dict)  # OutputType: {}
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_generated_content(self, output_type: OutputType, content: GeneratedData):
        """Add generated content for a specific output type."""
        self.generated[output_type] = content
        self.updated_at = datetime.utcnow()

    def set_status(self, status: GeneratedContentStatus, reason: str = ""):
        """Set the status, update status_details, and update the updated_at timestamp."""
        self.status = status
        self.status_details = StatusDetail(
            status=status, created_at=datetime.utcnow(), reason=reason
        )
        self.updated_at = datetime.utcnow()
