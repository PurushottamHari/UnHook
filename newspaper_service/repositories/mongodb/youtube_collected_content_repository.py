from typing import List, Optional

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.youtube.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_collector_service.repositories.mongodb.adapters.youtube_collected_content_adapter import (
    YouTubeCollectedContentAdapter,
)
from data_collector_service.repositories.mongodb.models.youtube_collected_content_db_model import (
    YouTubeCollectedContentDBModel,
)
from injector import inject

from ..youtube_collected_content_repository import YouTubeCollectedContentRepository
from .config.database import MongoDB
from .config.settings import get_mongodb_settings


@injectable()
class MongoDBYouTubeCollectedContentRepository(YouTubeCollectedContentRepository):
    """MongoDB implementation of the YouTube collected content repository for newspaper service."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.settings = get_mongodb_settings()
        self.collection = mongodb.get_database()[
            self.settings.YOUTUBE_COLLECTED_CONTENT_COLLECTION_NAME
        ]

    def get_video_by_id(self, video_id: str) -> Optional[YouTubeVideoDetails]:
        """Retrieve a YouTube video by its ID."""
        doc = self.collection.find_one({"video_id": video_id})
        if not doc:
            return None

        db_model = YouTubeCollectedContentDBModel(**doc)
        return YouTubeCollectedContentAdapter.from_db_model(db_model)

    def get_videos_by_ids(self, video_ids: List[str]) -> List[YouTubeVideoDetails]:
        """Retrieve multiple YouTube videos by their IDs."""
        if not video_ids:
            return []

        cursor = self.collection.find({"video_id": {"$in": video_ids}})
        videos = []
        for doc in cursor:
            db_model = YouTubeCollectedContentDBModel(**doc)
            videos.append(YouTubeCollectedContentAdapter.from_db_model(db_model))
        return videos
