import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List
from uuid import uuid4

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging.models import Command
from commons.messaging.producer import MessageProducer

from ..models import (AggregatedSchedule, AggregatedScheduleStatus,
                      RunAggregatedScheduleCommand,
                      RunAggregatedSchedulePayload)
from ..repository import AggregatedScheduleRepository

logger = logging.getLogger(__name__)


@injectable()
class AggregatedScheduleService:
    """Service for orchestrating aggregated scheduled commands."""

    GLOBAL_KEY: str = "global"

    @inject
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
    ) -> AggregatedSchedule:
        """
        Create a new aggregated schedule and schedule its command.

        Args:
            keys: List of strings to form the unique aggregation key
            command: The business command to be aggregated and eventually executed
            delay_minutes: Delay before the command fires
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
            target_service=command.target_service,
            topic=command.topic,
            payload=RunAggregatedSchedulePayload(schedule_id=created_schedule.id),
        )
        await self.producer.schedule_command(trigger_command, scheduled_at)

        logger.info(
            f"🚀 Scheduled trigger '{trigger_command.action_name}' for {scheduled_at} on topic '{trigger_command.topic}' (Schedule ID: {created_schedule.id})"
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

        # Create a deep copy and apply updates explicitly
        updated_schedule = schedule.model_copy(deep=True)
        updated_schedule.payload = command.model_dump()
        updated_schedule.version += 1
        updated_schedule.updated_at = datetime.utcnow()

        await self.repository.update_schedule(updated_schedule)
        logger.info(
            f"📝 Updated business command for schedule: {updated_schedule.name} | {updated_schedule.id} (v{updated_schedule.version})"
        )

    async def execute_schedule(self, schedule_id: str) -> None:
        """
        Execute an aggregated schedule:
        1. Mark as processing
        2. Publish the underlying business command
        3. Mark as completed
        """
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            logger.error(f"❌ Cannot execute schedule {schedule_id}: Not found.")
            return

        if schedule.status != AggregatedScheduleStatus.INITIALIZED:
            logger.warning(
                f"⚠️ Schedule {schedule_id} is already in state {schedule.status}. Skipping."
            )
            return

        try:
            # 1. Mark as processing
            processing_schedule = schedule.model_copy(deep=True)
            processing_schedule.status = AggregatedScheduleStatus.PROCESSING

            # The unique constrain can be freed up now, adding the uuid as the key
            processing_schedule.aggregation_key = (
                f"{schedule.aggregation_key}:processed:{uuid4()}"
            )

            processing_schedule.version += 1
            processing_schedule.updated_at = datetime.utcnow()
            await self.repository.update_schedule(processing_schedule)

            # 2. Reconstruct and fire the original business command
            original_command = Command.model_validate(processing_schedule.payload)
            topic = f"{original_command.target_service}:commands"

            logger.info(
                f"Executing business command '{original_command.action_name}' for schedule {processing_schedule.id} on topic '{topic}'"
            )
            await self.producer.send_command(original_command)

            logger.info(
                f"✅ Completed aggregated schedule: {processing_schedule.name} | {processing_schedule.id} (v{processing_schedule.version})"
            )

        except Exception as e:
            logger.error(f"❌ Failed to execute schedule {schedule_id}: {e}")
            raise
