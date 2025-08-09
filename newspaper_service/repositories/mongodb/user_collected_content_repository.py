"""
MongoDB implementation of UserCollectedContentRepository.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional

from pymongo import UpdateOne

from data_collector_service.models.user_collected_content import (
    ContentStatus, UserCollectedContent)
from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import \
    CollectedContentAdapter
from data_collector_service.repositories.mongodb.models.collected_content_db_model import \
    CollectedContentDBModel

from ..user_collected_content_repository import UserCollectedContentRepository
from .config.database import MongoDB
from .config.settings import get_mongodb_settings


class MongoDBUserCollectedContentRepository(UserCollectedContentRepository):
    """MongoDB implementation of user collected content repository."""

    def __init__(self):
        self.settings = get_mongodb_settings()
        self.collection = MongoDB.get_database()[
            self.settings.USER_COLLECTED_CONTENT_COLLECTION_NAME
        ]

    def get_content_with_status(
        self,
        user_id: str,
        status: ContentStatus,
        before_time: Optional[datetime] = None,
    ) -> List[UserCollectedContent]:
        """Get content with specific status."""
        # NOTE: status is an Enum; store and query by its string value
        query: dict = {"user_id": user_id, "status": status.value}
        if before_time is not None:
            query["created_at"] = {"$lte": before_time.timestamp()}

        cursor = self.collection.find(query)
        results: List[UserCollectedContent] = []
        for doc in cursor:
            db_model = CollectedContentDBModel(**doc)
            results.append(CollectedContentAdapter.to_user_collected_content(db_model))
        return results

    def bulk_update_user_collected_content(
        self, contents: List[UserCollectedContent], session: Any = None
    ) -> int:
        if not contents:
            return 0
        operations = []
        for content in contents:
            db_model = CollectedContentAdapter.to_collected_content_db_model(content)
            update_doc = db_model.model_dump(by_alias=True, exclude_unset=True)
            _id = update_doc.pop("_id")
            operations.append(UpdateOne({"_id": _id}, {"$set": update_doc}))
        if not operations:
            return 0
        result = self.collection.bulk_write(operations, session=session)
        return result.modified_count or 0
