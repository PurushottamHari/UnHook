from typing import Any, ClassVar, Dict

from pydantic import BaseModel, Field

from commons.messaging import Command


class StartUserCollectionPayload(BaseModel):
    user_id: str


class StartUserCollectionCommand(Command):
    """Initial command to trigger collection for all sources of a user."""

    ACTION_NAME: ClassVar[str] = "start_user_collection"

    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    payload: StartUserCollectionPayload = Field(
        ..., description="Details for user collection start"
    )


class CollectYouTubeChannelForUserPayload(BaseModel):
    user_id: str
    channel_id: str
    max_videos: int


class CollectYouTubeChannelForUserCommand(Command):
    """Granular command for a single YouTube channel collection and processing."""

    ACTION_NAME: ClassVar[str] = "collect_youtube_channel_for_user"

    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    payload: CollectYouTubeChannelForUserPayload = Field(
        ..., description="Details for channel collection"
    )


class EnrichYouTubeVideoForUserPayload(BaseModel):
    user_id: str
    video_id: str
    user_collected_content_id: str
    channel_name: str


class EnrichYouTubeVideoForUserCommand(Command):
    ACTION_NAME: ClassVar[str] = "enrich_youtube_video_for_user"

    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    payload: EnrichYouTubeVideoForUserPayload = Field(
        ..., description="Details for video enrichment"
    )
