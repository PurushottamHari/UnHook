"""
MongoDB database model for users.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from .interests_db_model import InterestDBModel, NotInterestedDBModel
from .manual_config_db_model import ManualConfigDBModel


class UserDBModel(BaseModel):
    """Database model for users in MongoDB."""

    id: str = Field(alias="_id")  # MongoDB _id field
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    name: str = Field(..., min_length=1)
    created_at: str  # Stored as ISO format string with 'Z' suffix
    max_reading_time_per_day_mins: int = Field(..., gt=0)
    interested: List[InterestDBModel] = Field(default_factory=list)
    not_interested: List[NotInterestedDBModel] = Field(default_factory=list)
    manual_configs: ManualConfigDBModel = Field(default_factory=ManualConfigDBModel)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
