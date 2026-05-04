from datetime import datetime

from commons.messaging.aggregated_schedule.models import (
    AggregatedSchedule, AggregatedScheduleStatus, AggregatedStatusDetail)
from data_processing_service.repositories.mongodb.models.aggregated_schedule_db_model import (
    AggregatedScheduleDBModel, AggregatedStatusDetailDBModel)


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
            status_details=[
                AggregatedStatusDetailDBModel(
                    status=d.status,
                    details=d.details,
                    timestamp=d.timestamp.timestamp(),
                )
                for d in domain.status_details
            ],
            scheduled_at=domain.scheduled_at.timestamp(),
            version=domain.version,
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
            status_details=[
                AggregatedStatusDetail(
                    status=AggregatedScheduleStatus(d.status),
                    details=d.details,
                    timestamp=datetime.fromtimestamp(d.timestamp),
                )
                for d in db_model.status_details
            ],
            scheduled_at=datetime.fromtimestamp(db_model.scheduled_at),
            version=db_model.version,
            created_at=datetime.fromtimestamp(db_model.created_at),
            updated_at=datetime.fromtimestamp(db_model.updated_at),
        )
