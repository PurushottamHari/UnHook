"""
Model for paginated list response of newspapers.
"""

from typing import List

from pydantic import BaseModel, Field

from .newspaper import Newspaper
from .newspaper_response import NewspaperResponse


class NewspaperListData(BaseModel):
    """Data container for paginated list response."""

    list_response: List[NewspaperResponse] = Field(
        ..., description="List of newspapers"
    )
    hasNext: bool = Field(..., description="Whether more items exist after this page")


class NewspaperListResponse(BaseModel):
    """Response model for paginated list of newspapers."""

    data: NewspaperListData = Field(..., description="Paginated list data")
