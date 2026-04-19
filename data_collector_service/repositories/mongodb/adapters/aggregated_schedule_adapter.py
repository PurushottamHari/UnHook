from datetime import datetime

from commons.messaging.aggregated_schedule.models import (
    AggregatedSchedule, AggregatedScheduleStatus)
from data_collector_service.repositories.mongodb.models.aggregated_schedule_db_model import \
    AggregatedScheduleDBModel


class AggregatedScheduleAdapter:
    """Adapter to convert between AggregatedSchedule domain model and DB model."""

    @staticmethod
    def to_db_model(domain: AggregatedSchedule) -> AggregatedScheduleDBModel:
        return AggregatedScheduleDBModel(
            _id=domain.id,
            name=domain.name,
            aggregation_key=domain.aggregation_key,
            payload=domain.payload,
            status=domain.status,
            scheduled_at=domain.scheduled_at.timestamp(),
            created_at=domain.created_at.timestamp(),
            updated_at=domain.updated_at.timestamp(),
        )

    @staticmethod
    def from_db_model(db_model: AggregatedScheduleDBModel) -> AggregatedSchedule:
        return AggregatedSchedule(
            id=str(db_model.id),
            name=db_model.name,
            aggregation_key=db_model.aggregation_key,
            payload=db_model.payload,
            status=AggregatedScheduleStatus(db_model.status),
            scheduled_at=datetime.fromtimestamp(db_model.scheduled_at),
            created_at=datetime.fromtimestamp(db_model.created_at),
            updated_at=datetime.fromtimestamp(db_model.updated_at),
        )
