from typing import Any, Dict
from commons.messaging import Command
from pydantic import BaseModel, Field


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
