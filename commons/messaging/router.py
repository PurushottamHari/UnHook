from abc import ABC, abstractmethod

from commons.messaging.aggregated_schedule.models import \
    RunAggregatedSchedulePayload
from commons.messaging.aggregated_schedule.service import \
    AggregatedScheduleService
from commons.messaging.models import Command, Event


class BaseCommandRouter(ABC):
    """
    Abstract base class for routing commands.
    Handles common infrastructure commands and delegates domain commands to subclasses.
    """

    def __init__(self, aggregated_schedule_service: AggregatedScheduleService):
        self.aggregated_schedule_service = aggregated_schedule_service

    async def handle(self, command: Command):
        """Main entry point for command handling."""
        if command.action_name == "run_aggregated_schedule":
            print(
                f"📦 [BaseCommandRouter] Handling common command: {command.action_name}"
            )
            payload = RunAggregatedSchedulePayload.model_validate(command.payload)
            await self.aggregated_schedule_service.execute_schedule(payload.schedule_id)
            print(
                f"✅ [BaseCommandRouter] Aggregated schedule {payload.schedule_id} executed successfully"
            )
            return

        # Delegate to domain-specific handler
        await self.handle_domain_command(command)

    @abstractmethod
    async def handle_domain_command(self, command: Command):
        """Must be implemented by subclasses to handle service-specific commands."""
        pass


class BaseEventRouter(ABC):
    """
    Abstract base class for routing events.
    """

    async def handle(self, event: Event):
        """Main entry point for event handling."""
        await self.handle_domain_event(event)

    @abstractmethod
    async def handle_domain_event(self, event: Event):
        """Must be implemented by subclasses to handle service-specific events."""
        pass
