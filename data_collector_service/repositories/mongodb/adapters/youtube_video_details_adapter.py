from datetime import datetime

from data_collector_service.collectors.youtube.models.youtube_video_details import \
    YouTubeVideoDetails
from data_collector_service.repositories.mongodb.adapters.subtitle_adapter import \
    SubtitleDBAdapter
from data_collector_service.repositories.mongodb.models.youtube_video_details import \
    YouTubeVideoDetailsDB


class YouTubeVideoDetailsAdapter:
    """Adapts between YouTubeVideoDetails and YouTubeVideoDetailsDB."""

    @staticmethod
    def to_db_model(entity: YouTubeVideoDetails) -> YouTubeVideoDetailsDB:
        """Convert YouTubeVideoDetails to YouTubeVideoDetailsDB."""
        return YouTubeVideoDetailsDB(
            video_id=entity.video_id,
            title=entity.title,
            channel_id=entity.channel_id,
            channel_name=entity.channel_name,
            views=entity.views,
            description=entity.description,
            thumbnail=entity.thumbnail,
            release_date=(
                entity.release_date.timestamp() if entity.release_date else None
            ),
            created_at=entity.created_at.timestamp(),
            tags=entity.tags,
            categories=entity.categories,
            language=entity.language,
            duration_in_seconds=entity.duration_in_seconds,
            comments_count=entity.comments_count,
            likes_count=entity.likes_count,
            subtitles=SubtitleDBAdapter.to_db_model(entity.subtitles),
        )

    @staticmethod
    def from_db_model(db_model: YouTubeVideoDetailsDB) -> YouTubeVideoDetails:
        """Convert YouTubeVideoDetailsDB to YouTubeVideoDetails."""
        return YouTubeVideoDetails(
            video_id=db_model.video_id,
            title=db_model.title,
            channel_id=db_model.channel_id,
            channel_name=db_model.channel_name,
            views=db_model.views,
            description=db_model.description,
            thumbnail=db_model.thumbnail,
            release_date=(
                datetime.fromtimestamp(db_model.release_date)
                if db_model.release_date
                else None
            ),
            created_at=datetime.fromtimestamp(db_model.created_at),
            tags=db_model.tags,
            categories=db_model.categories,
            language=db_model.language,
            duration_in_seconds=db_model.duration_in_seconds,
            comments_count=db_model.comments_count,
            likes_count=db_model.likes_count,
            subtitles=SubtitleDBAdapter.from_db_model(db_model.subtitles),
        )
