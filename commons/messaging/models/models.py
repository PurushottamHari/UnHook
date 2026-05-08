from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageAttempt(BaseModel):
    """
    Metadata about a single processing attempt.
    """

    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    failed_error_code: str | None = None
    failed_error_message: str | None = None


class MessageContext(BaseModel):
    """
    Context for tracking retries and processing history.
    """

    retry_count: int = 0
    attempts: List[MessageAttempt] = Field(default_factory=list)


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
    context: MessageContext = Field(
        default_factory=MessageContext, description="Retry and attempt context"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        exclude=True,
        description="Broker-specific metadata (not serialized)",
    )
    topic: str = Field(..., description="The topic/channel this message belongs to")
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
