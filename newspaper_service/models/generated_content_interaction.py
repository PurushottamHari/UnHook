"""
Model for generated content interactions (like/dislike/report/save).
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class InteractionType(str, Enum):
    """Types of interactions users can have with content."""

    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    REPORT = "REPORT"
    SAVED = "SAVED"


class InteractionStatus(str, Enum):
    """Status of an interaction."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class InteractionTypeDetail(BaseModel):
    """Detail information about an interaction type change."""

    interaction_type: InteractionType
    created_at: datetime
    reason: str = ""


class StatusDetail(BaseModel):
    """Detail information about a status change."""

    status: InteractionStatus
    created_at: datetime
    reason: str = ""


class GeneratedContentInteraction(BaseModel):
    """Model representing a user's interaction with generated content."""

    id: UUID = Field(default_factory=uuid4)
    generated_content_id: str = Field(..., description="ID of the generated content")
    user_id: str = Field(..., description="ID of the user")
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    metadata: Optional[Dict[str, str]] = Field(
        default=None, description="Optional metadata (e.g., report reason)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: InteractionStatus = Field(
        default=InteractionStatus.ACTIVE, description="Status of the interaction"
    )
    type_details: List[InteractionTypeDetail] = Field(
        default_factory=list, description="History of interaction type changes"
    )
    status_details: List[StatusDetail] = Field(
        default_factory=list, description="History of status changes"
    )

    def set_interaction_type(
        self, interaction_type: InteractionType, reason: str = ""
    ) -> None:
        """Set interaction type and append to type_details with timestamp."""
        self.interaction_type = interaction_type
        self.type_details.append(
            InteractionTypeDetail(
                interaction_type=interaction_type,
                created_at=datetime.utcnow(),
                reason=reason,
            )
        )
        self.updated_at = datetime.utcnow()

    def set_status(self, status: InteractionStatus, reason: str = "") -> None:
        """Set status and append to status_details with timestamp."""
        self.status = status
        self.status_details.append(
            StatusDetail(
                status=status,
                created_at=datetime.utcnow(),
                reason=reason,
            )
        )
        self.updated_at = datetime.utcnow()

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v):
        """Validate created_at is a datetime object."""
        if not isinstance(v, datetime):
            raise ValueError("created_at must be a datetime object")
        return v

    @field_validator("updated_at")
    @classmethod
    def validate_updated_at(cls, v):
        """Validate updated_at is a datetime object."""
        if not isinstance(v, datetime):
            raise ValueError("updated_at must be a datetime object")
        return v

    @field_validator("status_details", mode="before")
    @classmethod
    def validate_status_details(cls, v):
        """Ensure status_details is always a list."""
        if v is None:
            return []
        return v

    @model_validator(mode="after")
    def initialize_type_details(self):
        """Initialize type_details with the initial interaction_type if empty."""
        if not self.type_details:
            if self.interaction_type and self.created_at:
                self.type_details = [
                    InteractionTypeDetail(
                        interaction_type=self.interaction_type,
                        created_at=self.created_at,
                        reason="",
                    )
                ]
        # Ensure status_details is always initialized
        if self.status_details is None:
            self.status_details = []
        return self

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z", UUID: str}
