from typing import ClassVar

from pydantic import BaseModel, Field

from commons.messaging import Command


class StartDataProcessingForUserCollectedContentPayload(BaseModel):
    user_id: str
    user_collected_content_id: str


class StartDataProcessingForUserCollectedContentCommand(Command):
    ACTION_NAME: ClassVar[str] = "start_data_processing_for_user_collected_content"
    action_name: str = ACTION_NAME
    target_service: str = "data_processing_service"
    topic: str = "data_processing_service:commands"
    payload: StartDataProcessingForUserCollectedContentPayload = Field(
        ...,
        description="Details for starting data processing for user collected content",
    )
