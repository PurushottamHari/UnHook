from typing import ClassVar

from pydantic import BaseModel, Field

from commons.messaging import Command


class StartUserCollectionPayload(BaseModel):
    user_id: str


class StartUserCollectionCommand(Command):
    ACTION_NAME: ClassVar[str] = "start_user_collection"
    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    topic: str = "data_collector_service.commands"
    payload: StartUserCollectionPayload = Field(
        ..., description="Details for user collection start"
    )
