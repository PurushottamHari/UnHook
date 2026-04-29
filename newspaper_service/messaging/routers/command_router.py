from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseCommandRouter, Command
from commons.messaging.aggregated_schedule import AggregatedScheduleService


@injectable()
class CommandRouter(BaseCommandRouter):
    @inject
    def __init__(
        self,
        aggregated_schedule_service: AggregatedScheduleService,
    ):
        super().__init__(aggregated_schedule_service)

    async def handle_domain_command(self, command: Command):
        try:
            match command.action_name:
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
