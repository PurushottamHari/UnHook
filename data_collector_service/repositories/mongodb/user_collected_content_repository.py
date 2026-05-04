"""
MongoDB implementation of the UserCollectedContentRepository interface.
"""

from typing import List, Optional

from injector import inject
from pymongo import UpdateOne

from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentSubStatus, UserCollectedContent)
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoDetails
from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import \
    CollectedContentAdapter
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from data_collector_service.repositories.mongodb.models.collected_content_db_model import \
    CollectedContentDBModel
from data_collector_service.repositories.mongodb.utils.optimistic_locking import \
    create_optimistic_locking_update_op
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from data_collector_service.services.collection.collectors.youtube.adapters.youtube_to_user_content_adapter import \
    YouTubeToUserContentAdapter


class MongoDBUserCollectedContentRepository(UserCollectedContentRepository):
    """MongoDB implementation of user collected content repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.settings = get_mongodb_settings()
        self.collection = mongodb.get_database()[self.settings.COLLECTION_NAME]
        # Create indexes
        self.collection.create_index([("user_id", 1), ("external_id", 1)], unique=True)

    def filter_already_collected_content(
        self, user_id: str, video_ids: List[str]
    ) -> List[str]:
        """Get list of video IDs that haven't been collected yet for a user."""
        # Find all videos that are already collected for this user
        cursor = self.collection.find(
            {"user_id": user_id, "external_id": {"$in": video_ids}}, {"external_id": 1}
        )
        collected_videos = list(cursor)
        collected_video_ids = {doc["external_id"] for doc in collected_videos}

        print(
            f"Filtered content for user {user_id}: {len(collected_video_ids)} already collected out of {len(video_ids)} total videos"
        )

        # Return list of video IDs that haven't been collected
        return [vid for vid in video_ids if vid not in collected_video_ids]

    def get_processed_content_with_moderation_passed(
        self, user_id: str
    ) -> List[UserCollectedContent]:
        """Fetch all documents that are in 'PROCESSING' status and sub_status is 'MODERATION_PASSED' for a user."""

        cursor = self.collection.find(
            {
                "user_id": user_id,
                "status": ContentStatus.PROCESSING,
                "sub_status": ContentSubStatus.MODERATION_PASSED,
            }
        )

        content_list = []
        for doc in cursor:
            db_model = CollectedContentDBModel(**doc)
            user_content = CollectedContentAdapter.to_user_collected_content(db_model)
            content_list.append(user_content)

        print(
            f"Found {len(content_list)} processed contents with moderation passed for user {user_id}"
        )
        return content_list

    def get_unprocessed_content_for_user(
        self, user_id: str
    ) -> List[UserCollectedContent]:
        """
        Get list of unprocessed content for a user.
        """
        cursor = self.collection.find(
            {"user_id": str(user_id), "status": ContentStatus.COLLECTED}
        )

        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_content_by_ids(self, content_ids: List[str]) -> List[UserCollectedContent]:
        """
        Get list of content by IDs from MongoDB.
        """
        cursor = self.collection.find({"_id": {"$in": content_ids}})

        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_content_by_external_id_and_status(
        self, external_id: str, status: ContentStatus
    ) -> List[UserCollectedContent]:
        """
        Get a list of user collected content by external ID and status from MongoDB.
        """
        cursor = self.collection.find({"external_id": external_id, "status": status})

        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_content_by_external_id(
        self, user_id: str, external_id: str
    ) -> Optional[UserCollectedContent]:
        """
        Get a user collected content by user ID and external ID from MongoDB.
        """
        doc = self.collection.find_one({"user_id": user_id, "external_id": external_id})
        if not doc:
            return None

        db_model = CollectedContentDBModel(**doc)
        return CollectedContentAdapter.to_user_collected_content(db_model)

    def upsert_user_collected_content_batch(
        self, user_collected_content_list: List[UserCollectedContent]
    ) -> None:
        """
        Update or insert a batch of UserCollectedContent items in MongoDB.
        Matches by user_id and external_id for upsert.
        """
        operations = []
        for content in user_collected_content_list:
            db_model = CollectedContentAdapter.to_collected_content_db_model(content)
            update_dict = db_model.model_dump(by_alias=True, exclude_unset=True)

            # Mongodb does not allow _id to be passed even if same in $set
            # We want to use the generated ID on insert, but keep existing ID on update
            if "_id" in update_dict:
                _id = update_dict.pop("_id")
            else:
                _id = db_model.id

            # Use centralized optimistic locking utility
            operations.append(
                create_optimistic_locking_update_op(
                    filter_query={
                        "user_id": content.user_id,
                        "external_id": content.external_id,
                    },
                    update_dict=update_dict,
                    version=content.version,
                    id_for_insert=_id,
                )
            )

        if operations:
            result = self.collection.bulk_write(operations)
            print(
                f"✅ [UserContentRepository] Upserted {len(user_collected_content_list)} items (Matched: {result.matched_count}, Upserted: {result.upserted_count})"
            )
