"""
Newspaper adapter for converting between domain and database models.
"""

from datetime import datetime, timezone

from ....models import (ConsideredContent, ConsideredContentStatus,
                        ConsideredContentStatusDetail, Newspaper,
                        NewspaperStatus, StatusDetail)
from ..models.newspaper_db_model import (ConsideredContentDBModel,
                                         ConsideredContentStatusDetailDBModel,
                                         NewspaperDBModel, StatusDetailDBModel)


class NewspaperAdapter:
    """Adapter for converting between newspaper domain and database models."""

    @staticmethod
    def to_db_model(newspaper: Newspaper) -> NewspaperDBModel:
        return NewspaperDBModel(
            id=str(newspaper.id),
            user_id=newspaper.user_id,
            status=newspaper.status.value,
            status_details=[
                NewspaperAdapter._status_detail_to_db_model(detail)
                for detail in newspaper.status_details
            ],
            considered_content_list=[
                NewspaperAdapter._considered_to_db_model(item)
                for item in newspaper.considered_content_list
            ],
            final_content_list=list(newspaper.final_content_list),
            reading_time_in_seconds=newspaper.reading_time_in_seconds,
            created_at=NewspaperAdapter._datetime_to_float(newspaper.created_at),
            updated_at=NewspaperAdapter._datetime_to_float(newspaper.updated_at),
        )

    @staticmethod
    def to_internal_model(db_model: NewspaperDBModel) -> Newspaper:
        return Newspaper(
            id=db_model.id,
            user_id=db_model.user_id,
            status=NewspaperStatus(db_model.status),
            status_details=[
                NewspaperAdapter._status_detail_to_internal_model(detail)
                for detail in db_model.status_details
            ],
            considered_content_list=[
                NewspaperAdapter._considered_to_internal_model(item)
                for item in db_model.considered_content_list
            ],
            final_content_list=list(db_model.final_content_list),
            reading_time_in_seconds=db_model.reading_time_in_seconds,
            created_at=NewspaperAdapter._float_to_datetime(db_model.created_at),
            updated_at=NewspaperAdapter._float_to_datetime(db_model.updated_at),
        )

    @staticmethod
    def _status_detail_to_db_model(detail: StatusDetail) -> StatusDetailDBModel:
        return StatusDetailDBModel(
            status=detail.status.value,
            created_at=NewspaperAdapter._datetime_to_float(detail.created_at),
            reason=detail.reason,
        )

    @staticmethod
    def _status_detail_to_internal_model(
        db_detail: StatusDetailDBModel,
    ) -> StatusDetail:
        return StatusDetail(
            status=NewspaperStatus(db_detail.status),
            created_at=NewspaperAdapter._float_to_datetime(db_detail.created_at),
            reason=db_detail.reason,
        )

    @staticmethod
    def _considered_to_db_model(
        item: ConsideredContent,
    ) -> ConsideredContentDBModel:
        return ConsideredContentDBModel(
            user_collected_content_id=item.user_collected_content_id,
            considered_content_status=item.considered_content_status.value,
            status_details=[
                ConsideredContentStatusDetailDBModel(
                    status=detail.status.value,
                    created_at=NewspaperAdapter._datetime_to_float(detail.created_at),
                    reason=detail.reason,
                )
                for detail in item.status_details
            ],
        )

    @staticmethod
    def _considered_to_internal_model(
        db_item: ConsideredContentDBModel,
    ) -> ConsideredContent:
        return ConsideredContent(
            user_collected_content_id=db_item.user_collected_content_id,
            considered_content_status=ConsideredContentStatus(
                db_item.considered_content_status
            ),
            status_details=[
                ConsideredContentStatusDetail(
                    status=ConsideredContentStatus(detail.status),
                    created_at=NewspaperAdapter._float_to_datetime(detail.created_at),
                    reason=detail.reason,
                )
                for detail in db_item.status_details
            ],
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
