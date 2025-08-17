"""
MongoDB database model for collected content.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SubStatusDetails(BaseModel):
    sub_status: str
    reason: str
    created_at: float


class StatusDetails(BaseModel):
    status: str
    reason: str
    created_at: float


class CollectedContentDBModel(BaseModel):
    """Database model for collected videos."""

    id: str = Field(alias="_id")  # MongoDB _id field
    external_id: str
    content_type: str
    user_id: str
    output_type: str
    created_at: float
    updated_at: float
    content_created_at: float
    status: str
    status_details: List[StatusDetails]
    sub_status: Optional[str] = None
    sub_status_details: List[SubStatusDetails] = []
    data: Dict[str, Any]

    class Config:
        populate_by_name = True
