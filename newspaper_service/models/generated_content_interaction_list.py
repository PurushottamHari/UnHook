"""
Model for paginated list response of generated content interactions.
"""

from typing import List

from pydantic import BaseModel, Field

from .generated_content_interaction import GeneratedContentInteraction


class GeneratedContentInteractionListData(BaseModel):
    """Data container for paginated list response."""

    list_response: List[GeneratedContentInteraction] = Field(
        ..., description="List of generated content interactions"
    )
    hasNext: bool = Field(..., description="Whether more items exist after this page")


class GeneratedContentInteractionListResponse(BaseModel):
    """Response model for paginated list of generated content interactions."""

    data: GeneratedContentInteractionListData = Field(
        ..., description="Paginated list data"
    )
