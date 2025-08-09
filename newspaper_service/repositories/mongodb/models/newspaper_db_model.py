"""
Newspaper database model for MongoDB (aligned to simplified dataclass domain).
"""

from typing import List

from pydantic import BaseModel, Field


class StatusDetailDBModel(BaseModel):
    status: str = Field(..., description="Status value")
    created_at: float = Field(..., description="UTC epoch seconds")
    reason: str = Field(default="", description="Status change reason")


class ConsideredContentStatusDetailDBModel(BaseModel):
    status: str = Field(..., description="Considered content status value")
    created_at: float = Field(..., description="UTC epoch seconds")
    reason: str = Field(default="", description="Status change reason")


class ConsideredContentDBModel(BaseModel):
    user_collected_content_id: str = Field(...)
    considered_content_status: str = Field(...)
    status_details: List[ConsideredContentStatusDetailDBModel] = Field(
        default_factory=list
    )


class NewspaperDBModel(BaseModel):
    id: str = Field(alias="_id", description="MongoDB _id field")
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Newspaper status")
    status_details: List[StatusDetailDBModel] = Field(default_factory=list)
    considered_content_list: List[ConsideredContentDBModel] = Field(
        default_factory=list
    )
    final_content_list: List[str] = Field(default_factory=list)
    reading_time_in_seconds: int = Field(
        default=0, description="Total reading time in seconds"
    )
    created_at: float = Field(..., description="UTC epoch seconds")
    updated_at: float = Field(..., description="UTC epoch seconds")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
