import logging

from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseEventRouter, Event

logger = logging.getLogger(__name__)


@injectable()
class EventRouter(BaseEventRouter):
    """Routes incoming events to the appropriate service logic."""

    @inject
    def __init__(self):
        super().__init__()

    async def handle_domain_event(self, event: Event):
        """Dispatches the event based on event_type."""
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
