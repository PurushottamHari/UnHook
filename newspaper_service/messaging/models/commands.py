from typing import ClassVar

from pydantic import BaseModel, Field

from commons.messaging import Command


class StartCollationForNewspaperPayload(BaseModel):
    """Payload for starting newspaper collation."""

    newspaper_id: str
    user_id: str


class StartCollationForNewspaperCommand(Command):
    """Command to start the collation process for a newspaper."""

    ACTION_NAME: ClassVar[str] = "start_collation_for_newspaper"

    action_name: str = ACTION_NAME
    target_service: str = "newspaper_service"
    topic: str = "newspaper_service:commands"
    payload: StartCollationForNewspaperPayload = Field(
        ..., description="Details for starting newspaper collation"
    )


class CreateNewspaperForUserPayload(BaseModel):
    """Payload for creating a newspaper for a user."""

    user_id: str


class CreateNewspaperForUserCommand(Command):
    """Command to create a newspaper for a user."""

    ACTION_NAME: ClassVar[str] = "create_newspaper_for_user"

    action_name: str = ACTION_NAME
    target_service: str = "newspaper_service"
    topic: str = "newspaper_service:commands"
    payload: CreateNewspaperForUserPayload = Field(
        ..., description="Details for creating a newspaper for a user"
    )
