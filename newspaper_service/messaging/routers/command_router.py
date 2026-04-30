from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseCommandRouter, Command
from commons.messaging.aggregated_schedule import AggregatedScheduleService

from ...services.collate_articles.collate_articles_for_newspaper_service import \
    CollateArticlesForNewspaperService
from ...services.create_newspaper.create_newspaper_for_user_service import \
    CreateNewspaperForUserService
from ..models.commands import (CreateNewspaperForUserCommand,
                               StartCollationForNewspaperCommand)


@injectable()
class CommandRouter(BaseCommandRouter):
    @inject
    def __init__(
        self,
        aggregated_schedule_service: AggregatedScheduleService,
        create_newspaper_for_user_service: CreateNewspaperForUserService,
        collate_articles_for_newspaper_service: CollateArticlesForNewspaperService,
    ):
        super().__init__(aggregated_schedule_service)
        self.create_newspaper_for_user_service = create_newspaper_for_user_service
        self.collate_articles_for_newspaper_service = (
            collate_articles_for_newspaper_service
        )

    async def handle_domain_command(self, command: Command):
        try:
            match command.action_name:
                case CreateNewspaperForUserCommand.action_name:
                    print("🚀 Handling CreateNewspaperForUserCommand")
                    typed_command = CreateNewspaperForUserCommand(
                        **command.model_dump()
                    )
                    await self.create_newspaper_for_user_service.execute(
                        user_id=typed_command.payload.user_id,
                    )
                    print("✅ Handled CreateNewspaperForUserCommand")
                case StartCollationForNewspaperCommand.action_name:
                    print("🚀 Handling StartCollationForNewspaperCommand")
                    typed_collation_command = StartCollationForNewspaperCommand(
                        **command.model_dump()
                    )
                    await self.collate_articles_for_newspaper_service.execute(
                        user_id=typed_collation_command.payload.user_id,
                        newspaper_id=typed_collation_command.payload.newspaper_id,
                    )
                    print("✅ Handled StartCollationForNewspaperCommand")
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
