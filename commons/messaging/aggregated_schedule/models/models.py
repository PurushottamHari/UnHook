from datetime import datetime
from enum import Enum
from typing import Any, Dict
from uuid import uuid4

from pydantic import BaseModel, Field

from commons.messaging import Command


class AggregatedScheduleStatus(str, Enum):
    INITIALIZED = "initialized"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AggregatedStatusDetail(BaseModel):
    """Detailed record of a status change."""

    status: AggregatedScheduleStatus
    details: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AggregatedSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    aggregation_key: str
    payload: Dict[str, Any]
    status: AggregatedScheduleStatus = AggregatedScheduleStatus.INITIALIZED
    status_details: list[AggregatedStatusDetail] = Field(default_factory=list)
    scheduled_at: datetime
    version: int = Field(default=1, description="Version for optimistic locking")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def set_status(self, status: AggregatedScheduleStatus, details: str | None = None):
        """Update status and append to history."""
        self.status = status
        self.status_details.append(
            AggregatedStatusDetail(status=status, details=details)
        )
        self.updated_at = datetime.utcnow()


class RunAggregatedSchedulePayload(BaseModel):
    """Payload for the generic aggregated schedule trigger."""

    schedule_id: str = Field(
        ..., description="The ID of the aggregated schedule to run"
    )


class RunAggregatedScheduleCommand(Command):
    """Generic command to trigger an aggregated schedule."""

    action_name: str = "run_aggregated_schedule"
    target_service: str = "data_collector_service"
    payload: RunAggregatedSchedulePayload = Field(
        ..., description="Details for the aggregated schedule trigger"
    )
