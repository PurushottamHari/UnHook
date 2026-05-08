from datetime import datetime, timezone

from ....models import NewspaperStatus, NewspaperV2, StatusDetail
from ..models.newspaper_db_model import StatusDetailDBModel
from ..models.newspaper_v2_db_model import NewspaperV2DBModel


class NewspaperV2Adapter:
    """Adapter for converting between NewspaperV2 domain and database models."""

    @staticmethod
    def to_db_model(newspaper: NewspaperV2) -> NewspaperV2DBModel:
        return NewspaperV2DBModel(
            id=str(newspaper.id),
            user_id=newspaper.user_id,
            status=newspaper.status.value,
            status_details=[
                NewspaperV2Adapter._status_detail_to_db_model(detail)
                for detail in newspaper.status_details
            ],
            reading_time_in_seconds=newspaper.reading_time_in_seconds,
            version=newspaper.version,
            created_at=NewspaperV2Adapter._datetime_to_float(newspaper.created_at),
            updated_at=NewspaperV2Adapter._datetime_to_float(newspaper.updated_at),
        )

    @staticmethod
    def to_internal_model(db_model: NewspaperV2DBModel) -> NewspaperV2:
        return NewspaperV2(
            id=db_model.id,
            user_id=db_model.user_id,
            status=NewspaperStatus(db_model.status),
            status_details=[
                NewspaperV2Adapter._status_detail_to_internal_model(detail)
                for detail in db_model.status_details
            ],
            reading_time_in_seconds=db_model.reading_time_in_seconds,
            version=db_model.version,
            created_at=NewspaperV2Adapter._float_to_datetime(db_model.created_at),
            updated_at=NewspaperV2Adapter._float_to_datetime(db_model.updated_at),
        )

    @staticmethod
    def _status_detail_to_db_model(detail: StatusDetail) -> StatusDetailDBModel:
        return StatusDetailDBModel(
            status=detail.status.value,
            created_at=NewspaperV2Adapter._datetime_to_float(detail.created_at),
            reason=detail.reason,
        )

    @staticmethod
    def _status_detail_to_internal_model(
        db_detail: StatusDetailDBModel,
    ) -> StatusDetail:
        return StatusDetail(
            status=NewspaperStatus(db_detail.status),
            created_at=NewspaperV2Adapter._float_to_datetime(db_detail.created_at),
            reason=db_detail.reason,
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
