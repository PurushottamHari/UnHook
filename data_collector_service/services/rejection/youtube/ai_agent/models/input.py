"""
Input model for content moderation.
"""

from typing import List

from pydantic import BaseModel, Field

from .content import ContentItem


class ModerationInput(BaseModel):
    """Input model for content moderation."""

    items: List[ContentItem] = Field(
        ..., description="List of content items to be moderated"
    )
    filter_preferences: List[str] = Field(
        ..., description="List of topics/content types that should be filtered out"
    )
