"""
Model for paginated list response of generated content.
"""

from typing import List

from pydantic import BaseModel, Field

from data_processing_service.models.generated_content import GeneratedContent


class GeneratedContentListData(BaseModel):
    """Data container for paginated list response."""

    list_response: List[GeneratedContent] = Field(
        ..., description="List of generated content"
    )
    hasNext: bool = Field(..., description="Whether more items exist after this page")


class GeneratedContentListResponse(BaseModel):
    """Response model for paginated list of generated content."""

    data: GeneratedContentListData = Field(
        ..., description="Paginated list data"
    )

