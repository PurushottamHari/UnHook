from typing import List

from pydantic import BaseModel, Field

from .newspaper_db_model import StatusDetailDBModel


class NewspaperV2DBModel(BaseModel):
    """Newspaper V2 database model for MongoDB with versioning."""

    id: str = Field(alias="_id", description="MongoDB _id field")
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Newspaper status")
    status_details: List[StatusDetailDBModel] = Field(default_factory=list)
    reading_time_in_seconds: int = Field(
        default=0, description="Total reading time in seconds"
    )
    version: int = Field(default=1, description="Version for optimistic locking")
    created_at: float = Field(..., description="UTC epoch seconds")
    updated_at: float = Field(..., description="UTC epoch seconds")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
