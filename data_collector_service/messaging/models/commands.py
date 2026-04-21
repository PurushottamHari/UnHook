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


class ProcessYoutubeChannelRejectionAggregationPayload(BaseModel):
    """Payload for the YouTube channel rejection aggregation command."""

    user_id: str = Field(..., description="The ID of the user")
    channel_name: str = Field(..., description="The name of the YouTube channel")
    user_collected_content_ids: List[str] = Field(
        default_factory=list, description="List of user collected content IDs"
    )


class ProcessYoutubeChannelRejectionAggregationCommand(Command):
    """Command to trigger the processing of aggregated video rejections for a YouTube channel."""

    ACTION_NAME: ClassVar[str] = "process_youtube_channel_rejection_aggregation"

    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    payload: ProcessYoutubeChannelRejectionAggregationPayload = Field(
        ..., description="Details for the YouTube channel rejection aggregation"
    )


class SubmitModeratedContentForProcessingPayload(BaseModel):
    user_id: str
    user_collected_content_id: str


class SubmitModeratedContentForProcessingCommand(Command):
    ACTION_NAME: ClassVar[str] = "submit_moderated_content_for_processing"
    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    payload: SubmitModeratedContentForProcessingPayload = Field(
        ..., description="Details for submitting moderated content for processing"
    )
