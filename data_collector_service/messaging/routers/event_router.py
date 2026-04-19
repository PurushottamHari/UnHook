from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import Event


@injectable()
class EventRouter:
    """Routes incoming events to the appropriate service logic."""

    @inject
    def __init__(self):
        pass

    async def handle(self, event: Event):
        """Dispatches the event based on event_type."""
        match event.event_type:
            # case "user_created":
            #    async def _handle_user_created(self, event: Event):
            #        user_id = event.payload.get("user_id")
            #        print(f"👁️ [EventRouter] Observed UserCreated for {user_id}. Auto-triggering collection...")
            #        self.data_collector_service.collect_for_user(user_id)
            case _:
                raise NotImplementedError(
                    f"Event '{event.event_type}' is unimplemented in EventRouter"
                )
