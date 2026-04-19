from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AggregatedStatusDetailDBModel(BaseModel):
    status: str
    details: Optional[str] = None
    timestamp: float


class AggregatedScheduleDBModel(BaseModel):
    """Database model for aggregated schedules in MongoDB."""

    id: Optional[str] = Field(None, alias="_id")
    name: str
    aggregation_key: str
    payload: Dict[str, Any]
    status: str
    status_details: list[AggregatedStatusDetailDBModel] = Field(default_factory=list)
    scheduled_at: float  # timestamp
    version: int
    created_at: float  # timestamp
    updated_at: float  # timestamp

    class Config:
        populate_by_name = True
