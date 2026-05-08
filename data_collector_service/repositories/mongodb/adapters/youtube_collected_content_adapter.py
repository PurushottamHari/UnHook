from datetime import datetime, timezone

from data_collector_service.models.youtube.youtube_video_details import (
    YouTubeVideoDetails, YouTubeVideoStatus, YouTubeVideoStatusDetail)
from data_collector_service.repositories.mongodb.adapters.subtitle_adapter import \
    SubtitleDBAdapter
from data_collector_service.repositories.mongodb.models.youtube_collected_content_db_model import (
    YouTubeCollectedContentDBModel, YouTubeVideoStatusDetailDB)


class YouTubeCollectedContentAdapter:
    """Adapter to convert between YouTubeVideoDetails entity and YouTubeCollectedContentDBModel."""

    @staticmethod
    def to_db_model(entity: YouTubeVideoDetails) -> YouTubeCollectedContentDBModel:
        """Convert domain entity to database model."""
        return YouTubeCollectedContentDBModel(
            id=entity.video_id,  # Use video_id as the primary key _id
            video_id=entity.video_id,
            title=entity.title,
            channel_id=entity.channel_id,
            channel_name=entity.channel_name,
            views=entity.views,
            description=entity.description,
            thumbnail=entity.thumbnail,
            release_date=(
                YouTubeCollectedContentAdapter._datetime_to_float(entity.release_date)
                if entity.release_date
                else None
            ),
            created_at=YouTubeCollectedContentAdapter._datetime_to_float(
                entity.created_at
            ),
            tags=entity.tags,
            categories=entity.categories,
            language=entity.language,
            duration_in_seconds=entity.duration_in_seconds,
            comments_count=entity.comments_count,
            likes_count=entity.likes_count,
            subtitles=SubtitleDBAdapter.to_db_model(entity.subtitles),
            status=entity.status.value,
            status_details=[
                YouTubeVideoStatusDetailDB(
                    status=detail.status.value,
                    created_at=YouTubeCollectedContentAdapter._datetime_to_float(
                        detail.created_at
                    ),
                    reason=detail.reason,
                )
                for detail in entity.status_details
            ],
        )

    @staticmethod
    def from_db_model(db_model: YouTubeCollectedContentDBModel) -> YouTubeVideoDetails:
        """Convert database model to domain entity."""
        return YouTubeVideoDetails(
            video_id=db_model.video_id,
            title=db_model.title,
            channel_id=db_model.channel_id,
            channel_name=db_model.channel_name,
            views=db_model.views,
            description=db_model.description,
            thumbnail=db_model.thumbnail,
            release_date=(
                YouTubeCollectedContentAdapter._float_to_datetime(db_model.release_date)
                if db_model.release_date
                else None
            ),
            created_at=YouTubeCollectedContentAdapter._float_to_datetime(
                db_model.created_at
            ),
            tags=db_model.tags,
            categories=db_model.categories,
            language=db_model.language,
            duration_in_seconds=db_model.duration_in_seconds,
            comments_count=db_model.comments_count,
            likes_count=db_model.likes_count,
            subtitles=SubtitleDBAdapter.from_db_model(db_model.subtitles),
            status=YouTubeVideoStatus(db_model.status),
            status_details=[
                YouTubeVideoStatusDetail(
                    status=YouTubeVideoStatus(detail.status),
                    created_at=YouTubeCollectedContentAdapter._float_to_datetime(
                        detail.created_at
                    ),
                    reason=detail.reason,
                )
                for detail in db_model.status_details
            ],
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        """Converts a datetime object to a UTC timestamp float."""
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        """Converts a UTC timestamp float back to a datetime object."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)
