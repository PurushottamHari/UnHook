"""
Model for paginated list response of generated content.
"""

from typing import List

from pydantic import BaseModel, Field

from data_processing_service.models.generated_content import GeneratedContent

from .generated_content_interaction import GeneratedContentInteraction
from .generated_content_response import GeneratedContentResponse


class GeneratedContentWithInteractions(BaseModel):
    """Generated content with its active user interactions."""

    generated_content: GeneratedContentResponse = Field(
        ..., description="The generated content object"
    )
    active_user_interactions: List[GeneratedContentInteraction] = Field(
        default_factory=list,
        description="List of active user interactions for this content",
    )

    @classmethod
    def from_generated_content_with_interactions(
        cls,
        content: GeneratedContent,
        interactions: List[GeneratedContentInteraction],
    ) -> "GeneratedContentWithInteractions":
        """Convert GeneratedContent and interactions to response model."""
        return cls(
            generated_content=GeneratedContentResponse.from_generated_content(content),
            active_user_interactions=interactions,
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
