from typing import Any, List, Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging.aggregated_schedule.models import (
    AggregatedSchedule, AggregatedScheduleStatus)
from commons.messaging.aggregated_schedule.repository import \
    AggregatedScheduleRepository
from data_processing_service.repositories.mongodb.adapters.aggregated_schedule_adapter import \
    AggregatedScheduleAdapter
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.models.aggregated_schedule_db_model import \
    AggregatedScheduleDBModel


@injectable()
class MongoDBAggregatedScheduleRepository(AggregatedScheduleRepository):
    """MongoDB implementation of the aggregated schedule repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.collection = mongodb.get_database()["aggregated_schedules"]

        # Create unique index on (name, aggregation_key, status)
        self.collection.create_index(
            [("name", 1), ("aggregation_key", 1), ("status", 1)], unique=True
        )

    async def get_active_schedule(
        self, name: str, aggregation_key: str
    ) -> Optional[AggregatedSchedule]:
        doc = self.collection.find_one(
            {
                "name": name,
                "aggregation_key": aggregation_key,
                "status": AggregatedScheduleStatus.INITIALIZED.value,
            }
        )
        if not doc:
            return None

        db_model = AggregatedScheduleDBModel(**doc)
        return AggregatedScheduleAdapter.from_db_model(db_model)

    async def get_by_id(self, schedule_id: str) -> Optional[AggregatedSchedule]:
        doc = self.collection.find_one({"_id": schedule_id})
        if not doc:
            return None

        db_model = AggregatedScheduleDBModel(**doc)
        return AggregatedScheduleAdapter.from_db_model(db_model)

    async def create_schedule(self, schedule: AggregatedSchedule) -> AggregatedSchedule:
        db_model = AggregatedScheduleAdapter.to_db_model(schedule)
        doc = db_model.model_dump(by_alias=True)

        self.collection.insert_one(doc)
        return schedule

    async def update_schedule(self, schedule: AggregatedSchedule) -> None:
        new_version = schedule.version
        old_version = new_version - 1

        db_model = AggregatedScheduleAdapter.to_db_model(schedule)
        doc = db_model.model_dump(by_alias=True)

        # Use optimistic locking
        result = self.collection.replace_one(
            {"_id": schedule.id, "version": old_version}, doc
        )

        if result.matched_count == 0:
            schedule.version = old_version
            raise ValueError(
                f"❌ Optimistic locking failed for AggregatedSchedule {schedule.id}: "
                f"Version mismatch (expected {old_version}) or document deleted."
            )

        print(
            f"✅ [MongoDB] Updated AggregatedSchedule {schedule.id} to version {schedule.version}"
        )
