from typing import ClassVar, List

from pydantic import BaseModel, Field

from commons.messaging import Command


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
