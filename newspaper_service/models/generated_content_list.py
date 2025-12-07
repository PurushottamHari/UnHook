"""
Model for paginated list response of generated content.
"""

from typing import List

from pydantic import BaseModel, Field

from data_processing_service.models.generated_content import GeneratedContent

from .generated_content_interaction import GeneratedContentInteraction


class GeneratedContentWithInteractions(BaseModel):
    """Generated content with its active user interactions."""

    generated_content: GeneratedContent = Field(
        ..., description="The generated content object"
    )
    active_user_interactions: List[GeneratedContentInteraction] = Field(
        default_factory=list,
        description="List of active user interactions for this content",
    )


class GeneratedContentListData(BaseModel):
    """Data container for paginated list response."""

    list_response: List[GeneratedContentWithInteractions] = Field(
        ..., description="List of generated content with interactions"
    )
    hasNext: bool = Field(..., description="Whether more items exist after this page")


class GeneratedContentListResponse(BaseModel):
    """Response model for paginated list of generated content."""

    data: GeneratedContentListData = Field(..., description="Paginated list data")
