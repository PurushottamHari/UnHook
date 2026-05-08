from typing import ClassVar

from pydantic import BaseModel, Field

from commons.messaging.models import Event


class UserCollectedContentReadyToUsedPayload(BaseModel):
    """Payload for the user collected content ready to be used event."""

    user_id: str = Field(..., description="The ID of the user")
    user_collected_content_id: str = Field(
        ..., description="The ID of the user collected content"
    )
    external_id: str = Field(
        ..., description="The external ID of the content (e.g., YouTube video ID)"
    )


class UserCollectedContentReadyToBeUsedEvent(Event):
    """Event emitted when a user collected content is ready to be used (processed)."""

    EVENT_TYPE: ClassVar[str] = "user_collected_content_ready_to_be_used"

    topic: str = "data_collector_service:events"
    event_type: str = EVENT_TYPE
    source_service: str = "data_collector_service"
    payload: UserCollectedContentReadyToUsedPayload = Field(
        ..., description="Details of the ready content"
    )
