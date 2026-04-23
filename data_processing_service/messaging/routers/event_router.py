import logging

from injector import inject

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
        # For now, DP service might not handle many external events directly
        # but this is where they would go.
        logger.info(f"🔔 [EventRouter] Received event: {event.event_type}")
        pass
