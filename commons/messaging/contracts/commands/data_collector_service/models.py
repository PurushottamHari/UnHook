from typing import ClassVar, Literal

from pydantic import BaseModel, Field

from commons.messaging import Command


class StartUserCollectionPayload(BaseModel):
    user_id: str


class StartUserCollectionCommand(Command):
    ACTION_NAME: ClassVar[str] = "start_user_collection"
    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    topic: str = "data_collector_service:commands"
    payload: StartUserCollectionPayload = Field(
        ..., description="Details for user collection start"
    )


class DiscoveredWebpageData(BaseModel):
    title: str
    webpage_content: str
    language: str
    url: str
    category_name: str


class DiscoveredContentData(BaseModel):
    discovered_webpage: DiscoveredWebpageData


class AddDiscoveredCollectedContentPayload(BaseModel):
    content_type: str
    user_id: str
    output_type: str
    data: DiscoveredContentData
    created_at: int
    content_created_at: int


class AddDiscoveredCollectedContentCommand(Command):
    ACTION_NAME: ClassVar[str] = "add_discovered_collected_content"
    action_name: str = ACTION_NAME
    target_service: str = "data_collector_service"
    topic: str = "data_collector_service:commands"
    payload: AddDiscoveredCollectedContentPayload = Field(
        ..., description="Details for adding discovered content"
    )
