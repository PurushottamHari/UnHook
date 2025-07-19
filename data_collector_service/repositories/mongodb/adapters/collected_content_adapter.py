"""
Adapter for converting between internal models and MongoDB models for collected content.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from data_collector_service.collectors.youtube.models.youtube_video_details import \
    YouTubeVideoDetails
from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentType, StatusDetail, SubStatusDetail,
    UserCollectedContent)
from data_collector_service.repositories.mongodb.adapters.youtube_video_details_adapter import \
    YouTubeVideoDetailsAdapter
from data_collector_service.repositories.mongodb.models.youtube_video_details import \
    YouTubeVideoDetailsDB

from ..models.collected_content_db_model import (CollectedContentDBModel,
                                                 StatusDetails,
                                                 SubStatusDetails)


class CollectedContentAdapter:
    """Adapter for converting between internal models and MongoDB models."""

    @staticmethod
    def to_collected_content_db_model(
        content: UserCollectedContent,
    ) -> CollectedContentDBModel:
        """Convert internal content dict to CollectedContentDBModel."""
        # Validate required fields
        external_id = content.external_id
        if not external_id:
            raise ValueError("external_id is required but was not provided")

        status = content.status

        status_details = [
            StatusDetails(
                status=detail.status,
                reason=detail.reason,
                created_at=CollectedContentAdapter._datetime_to_float(
                    detail.created_at
                ),
            )
            for detail in content.status_details
        ]

        data_db_model = {}
        if content.content_type == ContentType.YOUTUBE_VIDEO:
            video_details = content.data.get(ContentType.YOUTUBE_VIDEO)
            if isinstance(video_details, YouTubeVideoDetails):
                data_db_model[ContentType.YOUTUBE_VIDEO] = (
                    YouTubeVideoDetailsAdapter.to_db_model(video_details)
                )
            else:
                raise TypeError(
                    f"Expected YouTubeVideoDetails, but got {type(video_details)}"
                )
        else:
            raise TypeError(f"Npt implemented Content Type: {content.content_type}")

        # Handle sub_status and sub_status_details if present
        sub_status = content.sub_status if hasattr(content, "sub_status") else None
        sub_status_details = []
        if hasattr(content, "sub_status_details") and content.sub_status_details:
            for detail in content.sub_status_details:
                sub_status_details.append(
                    SubStatusDetails(
                        sub_status=str(detail.sub_status),
                        reason=detail.reason,
                        created_at=CollectedContentAdapter._datetime_to_float(
                            detail.created_at
                        ),
                    )
                )

        return CollectedContentDBModel(
            id=content.id,  # MongoDB _id field
            external_id=external_id,
            content_type=content.content_type,
            user_id=content.user_id,
            output_type=content.output_type,
            created_at=CollectedContentAdapter._datetime_to_float(content.created_at),
            updated_at=CollectedContentAdapter._datetime_to_float(content.updated_at),
            status=status,
            status_details=status_details,
            sub_status=sub_status,
            sub_status_details=sub_status_details,
            data=data_db_model,
        )

    @staticmethod
    def to_user_collected_content(
        db_model: CollectedContentDBModel,
    ) -> UserCollectedContent:
        """Convert CollectedContentDBModel to UserCollectedContent."""
        status_details = [
            StatusDetail(
                status=ContentStatus(detail.status),
                created_at=CollectedContentAdapter._float_to_datetime(
                    detail.created_at
                ),
                reason=detail.reason,
            )
            for detail in db_model.status_details
        ]

        data: Dict[str, Any]
        if db_model.content_type == ContentType.YOUTUBE_VIDEO:
            video_details_db_data = db_model.data.get(ContentType.YOUTUBE_VIDEO)
            if not video_details_db_data:
                raise ValueError("YouTube video data not found in db_model")

            video_details_db = YouTubeVideoDetailsDB(**video_details_db_data)
            video_details = YouTubeVideoDetailsAdapter.from_db_model(video_details_db)
            data = {ContentType.YOUTUBE_VIDEO: video_details}
        else:
            raise TypeError(f"Npt implemented Content Type: {db_model.content_type}")

        # Handle sub_status and sub_status_details
        sub_status = getattr(db_model, "sub_status", None)
        sub_status_details = []
        if hasattr(db_model, "sub_status_details") and db_model.sub_status_details:
            for detail in db_model.sub_status_details:
                sub_status_details.append(
                    SubStatusDetail(
                        sub_status
                        == detail.sub_status,  # Reuse StatusDetail for sub_status
                        created_at=CollectedContentAdapter._float_to_datetime(
                            detail.created_at
                        ),
                        reason=detail.reason,
                    )
                )

        return UserCollectedContent(
            id=db_model.id,
            content_type=db_model.content_type,
            user_id=db_model.user_id,
            external_id=db_model.external_id,
            output_type=db_model.output_type,
            status=ContentStatus(db_model.status),
            status_details=status_details,
            data=data,
            sub_status=sub_status,
            sub_status_details=sub_status_details,
            created_at=CollectedContentAdapter._float_to_datetime(db_model.created_at),
            updated_at=CollectedContentAdapter._float_to_datetime(db_model.updated_at),
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        """Converts a datetime object to a UTC timestamp float."""
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        """Converts a UTC timestamp float back to a datetime object."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)
