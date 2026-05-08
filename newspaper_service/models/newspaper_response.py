"""
Pydantic response models for Newspaper with Unix timestamp serialization.
"""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from .newspaper import (ConsideredContent, ConsideredContentStatus,
                        ConsideredContentStatusDetail, Newspaper,
                        NewspaperStatus, StatusDetail)


class StatusDetailResponse(BaseModel):
    """Response model for StatusDetail with Unix timestamp."""

    status: str
    created_at: float = Field(..., description="Unix timestamp in seconds")
    reason: str = ""


class ConsideredContentStatusDetailResponse(BaseModel):
    """Response model for ConsideredContentStatusDetail with Unix timestamp."""

    status: str
    created_at: float = Field(..., description="Unix timestamp in seconds")
    reason: str = ""


class ConsideredContentResponse(BaseModel):
    """Response model for ConsideredContent with Unix timestamp serialization."""

    user_collected_content_id: str
    considered_content_status: str
    status_details: List[ConsideredContentStatusDetailResponse] = Field(
        default_factory=list
    )


class NewspaperResponse(BaseModel):
    """Pydantic response model for Newspaper with Unix timestamp serialization."""

    id: str
    user_id: str
    created_at: float = Field(..., description="Unix timestamp in seconds")
    updated_at: float = Field(..., description="Unix timestamp in seconds")
    status: str
    status_details: List[StatusDetailResponse] = Field(default_factory=list)
    considered_content_list: List[ConsideredContentResponse] = Field(
        default_factory=list
    )
    final_content_list: List[str] = Field(default_factory=list)
    reading_time_in_seconds: int = 0

    @classmethod
    def from_newspaper(cls, newspaper: Newspaper) -> "NewspaperResponse":
        """Convert Newspaper dataclass to response model."""

        # Convert datetime to Unix timestamp
        def datetime_to_timestamp(dt: datetime) -> float:
            return dt.astimezone(timezone.utc).timestamp()

        # Convert status details
        status_details_response = [
            StatusDetailResponse(
                status=detail.status.value,
                created_at=datetime_to_timestamp(detail.created_at),
                reason=detail.reason,
            )
            for detail in newspaper.status_details
        ]

        # Convert considered content list
        considered_content_response = [
            ConsideredContentResponse(
                user_collected_content_id=item.user_collected_content_id,
                considered_content_status=item.considered_content_status.value,
                status_details=[
                    ConsideredContentStatusDetailResponse(
                        status=detail.status.value,
                        created_at=datetime_to_timestamp(detail.created_at),
                        reason=detail.reason,
                    )
                    for detail in item.status_details
                ],
            )
            for item in newspaper.considered_content_list
        ]

        return cls(
            id=newspaper.id,
            user_id=newspaper.user_id,
            created_at=datetime_to_timestamp(newspaper.created_at),
            updated_at=datetime_to_timestamp(newspaper.updated_at),
            status=newspaper.status.value,
            status_details=status_details_response,
            considered_content_list=considered_content_response,
            final_content_list=newspaper.final_content_list,
            reading_time_in_seconds=newspaper.reading_time_in_seconds,
        )
