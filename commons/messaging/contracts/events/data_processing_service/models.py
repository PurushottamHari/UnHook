from typing import ClassVar

from pydantic import BaseModel, Field

from commons.messaging.models import Event


class GeneratedYoutubeContentArticleReadyPayload(BaseModel):
    """Payload for the YouTube content article generated event."""

    user_id: str = Field(..., description="The ID of the user")
    generated_content_id: str = Field(
        ..., description="The ID of the generated content"
    )
    external_id: str = Field(
        ..., description="The external ID of the content (e.g., YouTube video ID)"
    )


class GeneratedYoutubeContentArticleReadyEvent(Event):
    """Event emitted when a YouTube content article has been successfully generated."""

    EVENT_TYPE: ClassVar[str] = "generated_youtube_content_article_ready"

    topic: str = "data_processing_service:events"
    event_type: str = EVENT_TYPE
    source_service: str = "data_processing_service"
    payload: GeneratedYoutubeContentArticleReadyPayload = Field(
        ..., description="Details of the generated article"
    )
