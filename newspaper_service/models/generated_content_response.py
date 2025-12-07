"""
Pydantic response models for GeneratedContent with Unix timestamp serialization.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)


class StatusDetailResponse(BaseModel):
    """Response model for StatusDetail with Unix timestamp."""

    status: str
    created_at: float = Field(..., description="Unix timestamp in seconds")
    reason: str = ""


class GeneratedDataResponse(BaseModel):
    """Response model for GeneratedData."""

    markdown_string: str = ""
    string: str = ""


class CategoryInfoResponse(BaseModel):
    """Response model for CategoryInfo."""

    category: str
    category_description: str = ""
    category_tags: List[str] = Field(default_factory=list)
    shelf_life: Optional[str] = None
    geography: Optional[str] = None


class GeneratedContentResponse(BaseModel):
    """Pydantic response model for GeneratedContent with Unix timestamp serialization."""

    id: str
    external_id: str
    content_type: str
    status: str
    content_generated_at: float = Field(..., description="Unix timestamp in seconds")
    status_details: List[StatusDetailResponse] = Field(default_factory=list)
    category: Optional[CategoryInfoResponse] = None
    generated: Dict[str, GeneratedDataResponse] = Field(default_factory=dict)
    reading_time_seconds: int = 0
    created_at: float = Field(..., description="Unix timestamp in seconds")
    updated_at: float = Field(..., description="Unix timestamp in seconds")

    @classmethod
    def from_generated_content(
        cls, content: GeneratedContent
    ) -> "GeneratedContentResponse":
        """Convert GeneratedContent dataclass to response model."""

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
            for detail in content.status_details
        ]

        # Convert generated data
        generated_response = {
            k: GeneratedDataResponse(
                markdown_string=v.markdown_string,
                string=v.string,
            )
            for k, v in content.generated.items()
        }

        # Convert category
        category_response = None
        if content.category:
            category_response = CategoryInfoResponse(
                category=content.category.category.value,
                category_description=content.category.category_description,
                category_tags=content.category.category_tags,
                shelf_life=(
                    content.category.shelf_life.value
                    if content.category.shelf_life
                    else None
                ),
                geography=content.category.geography,
            )

        return cls(
            id=content.id,
            external_id=content.external_id,
            content_type=content.content_type.value,
            status=content.status.value,
            content_generated_at=datetime_to_timestamp(content.content_generated_at),
            status_details=status_details_response,
            category=category_response,
            generated=generated_response,
            reading_time_seconds=content.reading_time_seconds,
            created_at=datetime_to_timestamp(content.created_at),
            updated_at=datetime_to_timestamp(content.updated_at),
        )
