from commons.messaging.aggregated_schedule.models import (
    AggregatedSchedule, AggregatedStatusDetail)

from ..models.aggregated_schedule_db_model import (
    AggregatedScheduleDBModel, AggregatedStatusDetailDBModel)


class AggregatedScheduleAdapter:
    """Adapter for converting between domain model and database model."""

    @staticmethod
    def to_db_model(schedule: AggregatedSchedule) -> AggregatedScheduleDBModel:
        return AggregatedScheduleDBModel(
            _id=schedule.id,
            name=schedule.name,
            aggregation_key=schedule.aggregation_key,
            payload=schedule.payload,
            status=schedule.status.value,
            status_details=[
                AggregatedStatusDetailDBModel(
                    status=sd.status.value, details=sd.details, timestamp=sd.timestamp
                )
                for sd in schedule.status_details
            ],
            scheduled_at=schedule.scheduled_at,
            version=schedule.version,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at,
        )

    @staticmethod
    def from_db_model(db_model: AggregatedScheduleDBModel) -> AggregatedSchedule:
        return AggregatedSchedule(
            id=db_model.id,
            name=db_model.name,
            aggregation_key=db_model.aggregation_key,
            payload=db_model.payload,
            status=db_model.status,
            status_details=[
                AggregatedStatusDetail(
                    status=sd.status, details=sd.details, timestamp=sd.timestamp
                )
                for sd in db_model.status_details
            ],
            scheduled_at=db_model.scheduled_at,
            version=db_model.version,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )
