from typing import ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from commons.messaging import Event


class CandidateLinksPayload(BaseModel):
    """Links associated with a candidate."""

    user_collected_content_id: Optional[str] = None
    generated_content_id: Optional[str] = None
    generated_content_id_list: List[str] = Field(default_factory=list)


class ContentAddedToNewspaperPayload(BaseModel):
    """Payload for content added to a newspaper."""

    newspaper_id: str
    linked_id: str
    links: CandidateLinksPayload


class ContentAddedToNewspaperEvent(Event):
    """Event generated when content is added to a newspaper."""

    EVENT_TYPE: ClassVar[str] = "CONTENT_ADDED_TO_NEWSPAPER"

    event_type: str = EVENT_TYPE
    topic: str = "newspaper_service:events"
    payload: ContentAddedToNewspaperPayload = Field(
        ..., description="Details of the content added to the newspaper"
    )
