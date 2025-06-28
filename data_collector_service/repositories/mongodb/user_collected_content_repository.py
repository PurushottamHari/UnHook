"""
MongoDB implementation of the UserCollectedContentRepository interface.
"""

from typing import List
from data_collector_service.repositories.user_collected_content_repository import UserCollectedContentRepository
from data_collector_service.repositories.mongodb.config.settings import get_mongodb_settings
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import CollectedContentAdapter
from data_collector_service.collectors.youtube.adapters.youtube_to_user_content_adapter import YouTubeToUserContentAdapter
from data_collector_service.collectors.youtube.models.youtube_video_details import YouTubeVideoDetails
from data_collector_service.models.user_collected_content import UserCollectedContent, ContentStatus, ContentSubStatus
from data_collector_service.repositories.mongodb.models.collected_content_db_model import CollectedContentDBModel


class MongoDBUserCollectedContentRepository(UserCollectedContentRepository):
    """MongoDB implementation of user collected content repository."""
    
    def __init__(self):
        self.settings = get_mongodb_settings()
        self.collection = MongoDB.get_database()[self.settings.COLLECTION_NAME]
        # Create indexes
        self.collection.create_index([("user_id", 1), ("external_id", 1)], unique=True)
    
    def filter_already_collected_content(self, user_id: str, video_ids: List[str]) -> List[str]:
        """Get list of video IDs that haven't been collected yet for a user."""
        # Find all videos that are already collected for this user
        cursor = self.collection.find(
            {"user_id": user_id, "external_id": {"$in": video_ids}},
            {"external_id": 1}
        )
        collected_videos = list(cursor)
        collected_video_ids = {doc["external_id"] for doc in collected_videos}
        
        print(f"Filtered content for user {user_id}: {len(collected_video_ids)} already collected out of {len(video_ids)} total videos")
        
        # Return list of video IDs that haven't been collected
        return [vid for vid in video_ids if vid not in collected_video_ids]
    
    def add_collected_videos(self, videos: List[UserCollectedContent], user_id: str) -> None:
        """Add collected videos to the user's history."""
        if not videos:
            print(f"No videos to add for user {user_id}")
            return
            
        # Convert to database models
        collected_models = [
            CollectedContentAdapter.to_collected_content_db_model(content)
            for content in videos
        ]
        
        # Insert all documents
        if collected_models:
            result = self.collection.insert_many(
                [model.model_dump(by_alias=True) for model in collected_models]
            )
            print(f"Successfully added {len(result.inserted_ids)} videos to MongoDB for user {user_id}")

    def get_processed_content_with_moderation_passed(self, user_id: str) -> List[UserCollectedContent]:
        """Fetch all documents that are in 'PROCESSING' status and sub_status is 'MODERATION_PASSED' for a user."""
        
        cursor = self.collection.find({
            "user_id": user_id,
            "status": ContentStatus.PROCESSING,
            "sub_status": ContentSubStatus.MODERATION_PASSED
        })

        content_list = []
        for doc in cursor:
            db_model = CollectedContentDBModel(**doc)
            user_content = CollectedContentAdapter.to_user_collected_content(db_model)
            content_list.append(user_content)

        print(f"Found {len(content_list)} processed contents with moderation passed for user {user_id}")
        return content_list
        