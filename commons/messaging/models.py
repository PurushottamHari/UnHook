from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """
    Base model for all messages (events and commands).
    Provides common metadata needed for tracking and processing.
    """

    message_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the message"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Time the message was created"
    )
    correlation_id: UUID | None = Field(
        default=None,
        description="Identifier to trace a sequence of messages across services",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="The core data of the message"
    )


class Command(BaseMessage):
    """
    Represents an intent or request for a service to perform an action.
    Targeted explicitly at a specific service or capability.
    """

    target_service: str = Field(
        ..., description="The service expected to handle this command"
    )
    action_name: str = Field(
        ..., description="The specific action the service should take"
    )


class Event(BaseMessage):
    """
    Represents a fact or something that has happened.
    Broadcasted to any interested consumers.
    """

    source_service: str = Field(..., description="The service that emitted this event")
    event_type: str = Field(..., description="The type/name of the event that occurred")
