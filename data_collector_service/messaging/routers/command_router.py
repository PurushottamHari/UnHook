from commons.messaging import Command

from data_collector_service.infra.dependency_injection.injectable import injectable
from data_collector_service.services.collection.collection_service import (
    CollectionService,
)
from data_collector_service.services.rejection.reject_content_service import (
    RejectContentService,
)
from injector import inject


@injectable()
class CommandRouter:
    """Routes incoming commands to the appropriate service logic."""

    @inject
    def __init__(
        self,
        collection_service: CollectionService,
        reject_content_service: RejectContentService,
    ):
        self.collection_service = collection_service
        self.reject_content_service = reject_content_service

    async def handle(self, command: Command):
        """Dispatches the command based on action_name."""
        match command.action_name:
            case "collect_data":
                print(f"🎬 [CommandRouter] Starting collect_data command")
                self.collection_service.collect_for_user(command.payload["user_id"])
                print("✅ [CommandRouter] collect_data command completed")
            case "reject_content":
                print(f"🎬 [CommandRouter] Starting reject_content command")
                await self.reject_content_service.reject(command.payload["user_id"])
                print("✅ [CommandRouter] reject_content command completed")
            case _:
                raise NotImplementedError(
                    f"Command '{command.action_name}' is unimplemented in CommandRouter"
                )
