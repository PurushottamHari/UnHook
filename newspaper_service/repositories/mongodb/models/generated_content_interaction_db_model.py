"""
MongoDB database model for generated content interactions.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class InteractionTypeDetailDBModel(BaseModel):
    """Database model for interaction type detail."""

    interaction_type: str = Field(..., description="Interaction type value")
    created_at: float = Field(..., description="UTC epoch seconds")
    reason: str = Field(default="", description="Type change reason")


class GeneratedContentInteractionDBModel(BaseModel):
    """Database model for generated content interactions in MongoDB."""

    id: str = Field(alias="_id", description="MongoDB _id field")
    generated_content_id: str = Field(..., description="ID of the generated content")
    user_id: str = Field(..., description="ID of the user")
    interaction_type: str = Field(..., description="Type of interaction")
    metadata: Optional[Dict[str, str]] = Field(
        default=None, description="Optional metadata (e.g., report reason)"
    )
    created_at: float = Field(..., description="UTC epoch seconds")
    updated_at: float = Field(..., description="UTC epoch seconds")
    status: str = Field(default="ACTIVE", description="Status of the interaction")
    type_details: List[InteractionTypeDetailDBModel] = Field(
        default_factory=list, description="History of interaction type changes"
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
