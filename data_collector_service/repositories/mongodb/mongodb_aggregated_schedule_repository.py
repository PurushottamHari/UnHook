from typing import Any, List, Optional

from injector import inject

from commons.messaging.aggregated_schedule.models import (
    AggregatedSchedule, AggregatedScheduleStatus)
from commons.messaging.aggregated_schedule.repository import \
    AggregatedScheduleRepository
from data_collector_service.repositories.mongodb.adapters.aggregated_schedule_adapter import \
    AggregatedScheduleAdapter
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from data_collector_service.repositories.mongodb.models.aggregated_schedule_db_model import \
    AggregatedScheduleDBModel


class MongoDBAggregatedScheduleRepository(AggregatedScheduleRepository):
    """MongoDB implementation of the aggregated schedule repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.settings = get_mongodb_settings()
        self.collection = mongodb.get_database()["aggregated_schedules"]

        # Create unique index on (name, aggregation_key, status)
        # Note: We include status to allow multiple schedules for the same name/key over time,
        # but only one per status (e.g., only one 'initialized' at a time).
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
        # Use the version as it was before the domain logic incremented it for the query filter
        # Wait, if the domain logic incremented it, then we should use version - 1 as the filter.
        # Actually, it's cleaner if the service passes the version it read, but since we are inside the model,
        # we can just assume the current version in the object is the NEW one.

        new_version = schedule.version
        old_version = new_version - 1

        db_model = AggregatedScheduleAdapter.to_db_model(schedule)
        doc = db_model.model_dump(by_alias=True)

        # Use optimistic locking: filter by ID and the version we read (before increment)
        result = self.collection.replace_one(
            {"_id": schedule.id, "version": old_version}, doc
        )

        if result.matched_count == 0:
            # Restore version on failure so the caller knows it didn't advance
            schedule.version = old_version
            raise ValueError(
                f"❌ Optimistic locking failed for AggregatedSchedule {schedule.id}: "
                f"Version mismatch (expected {old_version}) or document deleted."
            )

        print(
            f"✅ [MongoDB] Updated AggregatedSchedule {schedule.id} to version {schedule.version}"
        )
