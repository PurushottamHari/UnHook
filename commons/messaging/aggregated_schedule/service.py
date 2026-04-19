import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from commons.messaging import Command, MessageProducer

from .models import (AggregatedSchedule, AggregatedScheduleStatus,
                     RunAggregatedScheduleCommand,
                     RunAggregatedSchedulePayload)
from .repository import AggregatedScheduleRepository

logger = logging.getLogger(__name__)


class AggregatedScheduleService:
    """Service for orchestrating aggregated scheduled commands."""

    def __init__(
        self, repository: AggregatedScheduleRepository, producer: MessageProducer
    ):
        self.repository = repository
        self.producer = producer

    async def get_active_schedule(
        self, name: str, keys: List[str]
    ) -> AggregatedSchedule | None:
        """Retrieve an active (initialized) schedule by name and composite key."""
        aggregation_key = ":".join(sorted(keys))
        return await self.repository.get_active_schedule(name, aggregation_key)

    async def create_schedule(
        self,
        keys: List[str],
        command: Command,
        delay_minutes: int,
        topic: str,
    ) -> AggregatedSchedule:
        """
        Create a new aggregated schedule and schedule its command.

        Args:
            keys: List of strings to form the unique aggregation key
            command: The business command to be aggregated and eventually executed
            delay_minutes: Delay before the command fires
            topic: Redis/Messaging topic for the command
        """
        name = command.action_name
        aggregation_key = ":".join(sorted(keys))
        scheduled_at = datetime.utcnow() + timedelta(minutes=delay_minutes)

        new_schedule = AggregatedSchedule(
            name=name,
            aggregation_key=aggregation_key,
            payload=command.model_dump(),
            status=AggregatedScheduleStatus.INITIALIZED,
            scheduled_at=scheduled_at,
        )

        created_schedule = await self.repository.create_schedule(new_schedule)

        # Schedule the generic trigger command
        trigger_command = RunAggregatedScheduleCommand(
            payload=RunAggregatedSchedulePayload(schedule_id=created_schedule.id)
        )
        await self.producer.schedule_command(topic, trigger_command, scheduled_at)

        logger.info(
            f"🚀 Scheduled trigger '{trigger_command.action_name}' for {scheduled_at} on topic '{topic}' (Schedule ID: {created_schedule.id})"
        )
        return created_schedule

    async def update_scheduled_command(
        self, schedule_id: str, command: Command
    ) -> None:
        """Update an existing schedule's underlying business command."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            logger.error(f"❌ Cannot update schedule {schedule_id}: Not found.")
            return

        schedule.payload = command.model_dump()
        schedule.updated_at = datetime.utcnow()
        await self.repository.update_schedule(schedule)
        logger.info(
            f"📝 Updated business command for schedule: {schedule.name} | {schedule.id}"
        )
