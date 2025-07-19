"""
Adapter for converting between internal models and MongoDB models for generated content.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from data_collector_service.models import ContentType
from data_processing_service.models.generated_content import (
    CategoryInfo, GeneratedContent, GeneratedContentStatus, GeneratedData,
    StatusDetail)
from data_processing_service.repositories.mongodb.models.generated_content_db_model import (
    CategoryInfoDBModel, GeneratedContentDBModel, GeneratedDataDBModel,
    StatusDetailDBModel)
from user_service.models import CategoryName


class GeneratedContentAdapter:
    """Adapter for converting between internal models and MongoDB models for generated content."""

    @staticmethod
    def to_generated_content_db_model(
        content: GeneratedContent,
    ) -> GeneratedContentDBModel:
        status_details_db = StatusDetailDBModel(
            status=content.status,
            created_at=GeneratedContentAdapter._datetime_to_float(
                content.status_details.created_at
            ),
            reason=content.status_details.reason,
        )
        generated_db = {
            k: GeneratedDataDBModel(markdown_string=v.markdown_string, string=v.string)
            for k, v in content.generated.items()
        }
        category_db = None
        if content.category is not None:
            category_db = CategoryInfoDBModel(
                category=content.category.category.value,
                category_description=content.category.category_description,
                category_tags=content.category.category_tags,
            )
        return GeneratedContentDBModel(
            id=content.id,
            external_id=content.external_id,
            content_type=content.content_type,
            generated=generated_db,
            created_at=GeneratedContentAdapter._datetime_to_float(content.created_at),
            updated_at=GeneratedContentAdapter._datetime_to_float(content.updated_at),
            content_generated_at=GeneratedContentAdapter._datetime_to_float(
                content.content_generated_at
            ),
            status=content.status,
            status_details=status_details_db,
            category=category_db,
        )

    @staticmethod
    def from_generated_content_db_model(
        db_model: GeneratedContentDBModel,
    ) -> GeneratedContent:
        status_details = StatusDetail(
            status=GeneratedContentStatus(db_model.status),
            created_at=GeneratedContentAdapter._float_to_datetime(
                db_model.status_details.created_at
            ),
            reason=db_model.status_details.reason,
        )
        generated = {
            k: GeneratedData(markdown_string=v.markdown_string, string=v.string)
            for k, v in db_model.generated.items()
        }
        category = None
        if db_model.category is not None:
            category = CategoryInfo(
                category=CategoryName(db_model.category.category),
                category_description=db_model.category.category_description,
                category_tags=db_model.category.category_tags,
            )
        return GeneratedContent(
            id=db_model.id,
            external_id=db_model.external_id,
            content_type=ContentType(db_model.content_type),
            generated=generated,
            created_at=GeneratedContentAdapter._float_to_datetime(db_model.created_at),
            updated_at=GeneratedContentAdapter._float_to_datetime(db_model.updated_at),
            content_generated_at=GeneratedContentAdapter._float_to_datetime(
                db_model.content_generated_at
            ),
            status=GeneratedContentStatus(db_model.status),
            status_details=status_details,
            category=category,
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
