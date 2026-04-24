from typing import ClassVar, List, Optional

from pydantic import BaseModel, Field

from commons.messaging import Command
from commons.messaging.contracts.commands.data_processing_service.models import (
    StartDataProcessingForUserCollectedContentCommand,
    StartDataProcessingForUserCollectedContentPayload)


class CategorizeGeneratedYoutubeContentAggregationPayload(BaseModel):
    generated_content_ids: List[str]


class CategorizeGeneratedYoutubeContentAggregationCommand(Command):
    ACTION_NAME: ClassVar[str] = "categorize_generated_youtube_content"

    action_name: str = ACTION_NAME
    target_service: str = "data_processing_service"
    payload: CategorizeGeneratedYoutubeContentAggregationPayload = Field(
        ..., description="Details for categorizing generated youtube content"
    )


class GenerateCompleteYoutubeContentPayload(BaseModel):
    generated_content_id: str


class GenerateCompleteYoutubeContentCommand(Command):
    ACTION_NAME: ClassVar[str] = "generate_complete_youtube_content"

    action_name: str = ACTION_NAME
    target_service: str = "data_processing_service"
    payload: GenerateCompleteYoutubeContentPayload = Field(
        ..., description="Details for generating complete youtube content"
    )
