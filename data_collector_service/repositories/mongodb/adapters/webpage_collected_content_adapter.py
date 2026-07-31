from datetime import datetime, timezone

from data_collector_service.models.webpage.webpage_collected_content import (
    WebpageCollectedContent, WebpageStatus, WebpageStatusDetail)
from data_collector_service.repositories.mongodb.models.webpage_collected_content_db_model import (
    WebpageCollectedContentDBModel, WebpageStatusDetailDB)


class WebpageCollectedContentAdapter:
    """Adapter to convert between WebpageCollectedContent entity and WebpageCollectedContentDBModel."""

    @staticmethod
    def to_db_model(entity: WebpageCollectedContent) -> WebpageCollectedContentDBModel:
        """Convert domain entity to database model."""
        return WebpageCollectedContentDBModel(
            id=entity.id,
            sha=entity.sha,
            url=entity.url,
            title=entity.title,
            webpage_content=entity.webpage_content,
            language=entity.language,
            category_name=entity.category_name,
            created_at=WebpageCollectedContentAdapter._datetime_to_float(
                entity.created_at
            ),
            content_created_at=WebpageCollectedContentAdapter._datetime_to_float(
                entity.content_created_at
            ),
            status=entity.status.value,
            status_details=[
                WebpageStatusDetailDB(
                    status=detail.status.value,
                    created_at=WebpageCollectedContentAdapter._datetime_to_float(
                        detail.created_at
                    ),
                    reason=detail.reason,
                )
                for detail in entity.status_details
            ],
            version=entity.version,
        )

    @staticmethod
    def from_db_model(
        db_model: WebpageCollectedContentDBModel,
    ) -> WebpageCollectedContent:
        """Convert database model to domain entity."""
        return WebpageCollectedContent(
            id=db_model.id,
            sha=db_model.sha,
            url=db_model.url,
            title=db_model.title,
            webpage_content=db_model.webpage_content,
            language=db_model.language,
            category_name=db_model.category_name,
            created_at=WebpageCollectedContentAdapter._float_to_datetime(
                db_model.created_at
            ),
            content_created_at=WebpageCollectedContentAdapter._float_to_datetime(
                db_model.content_created_at
            ),
            status=WebpageStatus(db_model.status),
            status_details=[
                WebpageStatusDetail(
                    status=WebpageStatus(detail.status),
                    created_at=WebpageCollectedContentAdapter._float_to_datetime(
                        detail.created_at
                    ),
                    reason=detail.reason,
                )
                for detail in db_model.status_details
            ],
            version=db_model.version,
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        """Converts a datetime object to a UTC timestamp float."""
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        """Converts a UTC timestamp float back to a datetime object."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)
