"""
Content item model for moderation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContentItem(BaseModel):
    """Model for a single content item to be moderated."""

    id: str = Field(..., description="Unique identifier for the content item")
    title: str = Field(..., description="Title of the content")
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
