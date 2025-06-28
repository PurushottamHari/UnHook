"""
Output model for content moderation.
"""
from typing import List
from pydantic import BaseModel, Field

class RejectedContent(BaseModel):
    """Model for a rejected content item with its reason."""
    id: str = Field(..., description="The json_id of the rejected content")
    reason: str = Field(..., description="The reason why the content was rejected")

class ModerationOutput(BaseModel):
    """Output model for content moderation."""
    rejected_items: List[RejectedContent]