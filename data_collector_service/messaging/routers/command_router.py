from commons.messaging import Command

from data_collector_service.infra.dependency_injection.injectable import injectable
from data_collector_service.services.collection.start_user_collection_service import (
    StartUserCollectionService,
)
from data_collector_service.services.rejection.reject_content_service import (
    RejectContentService,
)
from injector import inject
from pydantic import ValidationError

from data_collector_service.messaging.models.commands import (
    StartUserCollectionCommand,
    CollectYouTubeChannelForUserCommand,
)


@injectable()
class CommandRouter:
    """Routes incoming commands to the appropriate service logic."""

    @inject
    def __init__(
        self,
        start_user_collection_service: StartUserCollectionService,
        reject_content_service: RejectContentService,
    ):
        self.start_user_collection_service = start_user_collection_service
        self.reject_content_service = reject_content_service

    async def handle(self, command: Command):
        """Dispatches the command based on action_name and enforces strict typing."""
        try:
            match command.action_name:
                case "start_user_collection":
                    # Cast and validate the specific command model
                    start_command = StartUserCollectionCommand.model_validate(
                        command.model_dump()
                    )
                    print(f"🎬 [CommandRouter] Starting {start_command.action_name}")
                    await self.start_user_collection_service.start_collection(
                        start_command.payload.user_id
                    )
                    print(f"✅ [CommandRouter] {start_command.action_name} completed")

                case "collect_youtube_channel_for_user":
                    # Cast and validate the granular channel command
                    channel_command = (
                        CollectYouTubeChannelForUserCommand.model_validate(
                            command.model_dump()
                        )
                    )
                    print(f"🎬 [CommandRouter] Processing youtube channel collection")

                    print(
                        f"⚠️ [CommandRouter] Channel {channel_command.payload.channel_id} collection logic to be implemented"
                    )

                case "reject_content":
                    print(f"🎬 [CommandRouter] Starting reject_content command")
                    await self.reject_content_service.reject(command.payload["user_id"])
                    print("✅ [CommandRouter] reject_content command completed")

                case _:
                    raise NotImplementedError(
                        f"Command '{command.action_name}' is unimplemented in CommandRouter"
                    )
        except ValidationError as e:
            print(
                f"❌ [CommandRouter] Validation error for '{command.action_name}': {e}"
            )
            raise ValueError(
                f"Invalid command structure for '{command.action_name}': {e}"
            )
        except Exception as e:
            print(f"❌ [CommandRouter] Error handling '{command.action_name}': {e}")
            raise
