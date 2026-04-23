from typing import ClassVar, List, Optional

from pydantic import BaseModel, Field

from commons.messaging import Command
from data_collector_service.models.user_collected_content import ContentType


class ProcessModeratedContentPayload(BaseModel):
    user_id: str
    content_type: ContentType
    user_collected_content_id: str


class ProcessModeratedContentCommand(Command):
    ACTION_NAME: ClassVar[str] = "process_moderated_content"

    action_name: str = ACTION_NAME
    target_service: str = "data_processing_service"
    payload: ProcessModeratedContentPayload = Field(
        ..., description="Details for moderated content processing"
    )


class StartDataProcessingForUserCollectedContentPayload(BaseModel):
    user_id: str
    user_collected_content_id: str


class StartDataProcessingForUserCollectedContentCommand(Command):
    ACTION_NAME: ClassVar[str] = "start_data_processing_for_user_collected_content"

    action_name: str = ACTION_NAME
    target_service: str = "data_processing_service"
    payload: StartDataProcessingForUserCollectedContentPayload = Field(
        ...,
        description="Details for starting data processing for user collected content",
    )


class CategorizeGeneratedYoutubeContentAggregationPayload(BaseModel):
    generated_content_ids: List[str]


class CategorizeGeneratedYoutubeContentAggregationCommand(Command):
    ACTION_NAME: ClassVar[str] = "categorize_generated_youtube_content"

    action_name: str = ACTION_NAME
    target_service: str = "data_processing_service"
    payload: CategorizeGeneratedYoutubeContentAggregationPayload = Field(
        ..., description="Details for categorizing generated youtube content"
    )
