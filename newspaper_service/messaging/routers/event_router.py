from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseEventRouter, Event


@injectable()
class EventRouter(BaseEventRouter):
    @inject
    def __init__(self):
        pass

    async def handle_domain_event(self, event: Event):
        try:
            match event.event_type:
                case _:
                    raise NotImplementedError(f"Unknown event type: {event.event_type}")
        except ValidationError as e:
            print(f"❌ [EventRouter] Validation error for '{event.event_type}': {e}")
            raise
        except NotImplementedError as e:
            print(
                f"❌ [EventRouter] Not implemented error for '{event.event_type}': {e}"
            )
            raise
        except Exception as e:
            print(f"❌ [EventRouter] Error handling '{event.event_type}': {e}")
            raise
