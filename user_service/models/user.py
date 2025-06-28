"""
Main User model that combines all user-related data.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from .interests import Interest, NotInterested
from .manual_config import ManualConfig

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    name: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    max_reading_time_per_day_mins: int = Field(..., gt=0)
    interested: List[Interest] = Field(default_factory=list)
    not_interested: List[NotInterested] = Field(default_factory=list)
    manual_configs: ManualConfig = Field(default_factory=ManualConfig)

    @validator('created_at')
    def validate_created_at(cls, v):
        if not isinstance(v, datetime):
            raise ValueError("created_at must be a datetime object")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z',
            UUID: str
        } 