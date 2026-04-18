from typing import Any, Dict

from pydantic import BaseModel, Field

from commons.messaging import Command


class StartUserCollectionPayload(BaseModel):
    user_id: str


class StartUserCollectionCommand(Command):
    """Initial command to trigger collection for all sources of a user."""

    action_name: str = "start_user_collection"
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

    action_name: str = "collect_youtube_channel_for_user"
    target_service: str = "data_collector_service"
    payload: CollectYouTubeChannelForUserPayload = Field(
        ..., description="Details for channel collection"
    )


class EnrichYouTubeVideoForUserPayload(BaseModel):
    user_id: str
    video_id: str
    user_collected_content_id: str


class EnrichYouTubeVideoForUserCommand(Command):
    action_name: str = "enrich_youtube_video_for_user"
    target_service: str = "data_collector_service"
    payload: EnrichYouTubeVideoForUserPayload = Field(
        ..., description="Details for video enrichment"
    )
