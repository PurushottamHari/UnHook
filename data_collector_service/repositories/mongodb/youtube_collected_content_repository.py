from typing import List, Optional

from injector import inject
from pymongo import UpdateOne

from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoDetails
from data_collector_service.repositories.mongodb.adapters.youtube_collected_content_adapter import \
    YouTubeCollectedContentAdapter
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from data_collector_service.repositories.mongodb.models.youtube_collected_content_db_model import \
    YouTubeCollectedContentDBModel
from data_collector_service.repositories.mongodb.utils.optimistic_locking import \
    create_optimistic_locking_update_op
from data_collector_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository


class MongoDBYouTubeCollectedContentRepository(YouTubeCollectedContentRepository):
    """MongoDB implementation of the YouTube collected content repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.settings = get_mongodb_settings()
        self.collection = mongodb.get_database()[self.settings.YOUTUBE_COLLECTION_NAME]
        # Create unique index on video_id
        self.collection.create_index("video_id", unique=True)

    def upsert_videos(self, videos: List[YouTubeVideoDetails]) -> None:
        """Add or update YouTube videos in the shared collection."""
        if not videos:
            return

        operations = []
        for video in videos:
            db_model = YouTubeCollectedContentAdapter.to_db_model(video)
            video_dict = db_model.model_dump(by_alias=True)

            # Use centralized optimistic locking utility
            operations.append(
                create_optimistic_locking_update_op(
                    filter_query={"video_id": video.video_id},
                    update_dict=video_dict,
                    version=video.version,
                )
            )

        if operations:
            result = self.collection.bulk_write(operations)
            print(
                f"✅ [YouTubeRepository] Upserted {len(videos)} videos (Matched: {result.matched_count}, Upserted: {result.upserted_count})"
            )

    def get_video_by_id(self, video_id: str) -> YouTubeVideoDetails:
        """Retrieve a YouTube video by its ID."""
        doc = self.collection.find_one({"video_id": video_id})
        if not doc:
            raise ValueError(f"Video with ID {video_id} not found")

        db_model = YouTubeCollectedContentDBModel(**doc)
        return YouTubeCollectedContentAdapter.from_db_model(db_model)

    def filter_existing_videos(self, video_ids: List[str]) -> List[str]:
        """Get list of video IDs that haven't been added to the shared collection yet."""
        # Find all videos that are already in this shared collection
        cursor = self.collection.find({"video_id": {"$in": video_ids}}, {"video_id": 1})
        existing_docs = list(cursor)
        existing_video_ids = {doc["video_id"] for doc in existing_docs}

        print(
            f"🎬 [YouTubeRepository] Filtered raw content: {len(existing_video_ids)} already exist globally out of {len(video_ids)} requested"
        )

        return [vid for vid in video_ids if vid not in existing_video_ids]
