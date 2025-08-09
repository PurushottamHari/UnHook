"""
MongoDB implementation of newspaper repository.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from data_collector_service.models.user_collected_content import (
    ContentStatus, UserCollectedContent)

from ...models import Newspaper
from ..newspaper_repository import NewspaperRepository
from ..user_collected_content_repository import UserCollectedContentRepository
from .adapters.newspaper_adapter import NewspaperAdapter
from .config.database import MongoDB
from .config.settings import get_mongodb_settings


class MongoDBNewspaperRepository(NewspaperRepository):
    """MongoDB implementation of newspaper repository."""

    def __init__(
        self, user_collected_content_repository: UserCollectedContentRepository
    ):
        self.settings = get_mongodb_settings()
        self.database = MongoDB.get_database()
        self.collection = self.database[self.settings.NEWSPAPER_COLLECTION_NAME]
        self.logger = logging.getLogger(__name__)
        self.user_collected_content_repository = user_collected_content_repository

    def create_newspaper(
        self, newspaper: Newspaper, considered_user_contents: List[UserCollectedContent]
    ) -> Newspaper:
        """Create a newspaper and update user collected content in a single call."""
        try:
            db_model = NewspaperAdapter.to_db_model(newspaper)
            newspaper_doc = db_model.model_dump(by_alias=True)

            # Use a MongoDB transaction to atomically insert the newspaper and update collected content
            client = self.database.client
            with client.start_session() as session:
                with session.start_transaction():
                    insert_result = self.collection.insert_one(
                        newspaper_doc, session=session
                    )
                    self.logger.info(
                        f"Created newspaper with ID: {insert_result.inserted_id}"
                    )

                    if considered_user_contents:
                        modified = self.user_collected_content_repository.bulk_update_user_collected_content(
                            considered_user_contents, session=session
                        )
                        self.logger.info(
                            f"Updated {modified} user_collected_content items to PICKED_FOR_EVALUATION"
                        )
            return newspaper
        except Exception as e:
            self.logger.error(
                f"Error creating newspaper with aggregated updates: {str(e)}"
            )
            raise

    async def get_newspaper(self, newspaper_id: str) -> Optional[Newspaper]:
        """Get a newspaper by ID."""
        try:
            document = await self.collection.find_one({"_id": newspaper_id})
            if document:
                db_model = NewspaperDBModel(**document)  # type: ignore[name-defined]
                return NewspaperAdapter.to_internal_model(db_model)
            return None
        except Exception as e:
            self.logger.error(f"Error getting newspaper {newspaper_id}: {str(e)}")
            raise

    async def get_newspapers_by_user(self, user_id: str) -> List[Newspaper]:
        """Get all newspapers for a user."""
        try:
            cursor = self.collection.find({"user_id": user_id})
            newspapers = []
            async for document in cursor:
                db_model = NewspaperAdapter.to_internal_model(document)
                newspapers.append(db_model)
            return newspapers
        except Exception as e:
            self.logger.error(f"Error getting newspapers for user {user_id}: {str(e)}")
            raise

    async def get_newspapers_by_status(self, status: str) -> List[Newspaper]:
        """Get newspapers by status."""
        try:
            cursor = self.collection.find({"status": status})
            newspapers = []
            async for document in cursor:
                db_model = NewspaperAdapter.to_internal_model(document)
                newspapers.append(db_model)
            return newspapers
        except Exception as e:
            self.logger.error(f"Error getting newspapers by status {status}: {str(e)}")
            raise

    async def update_newspaper(self, newspaper: Newspaper) -> Newspaper:
        """Update a newspaper."""
        try:
            db_model = NewspaperAdapter.to_db_model(newspaper)
            result = await self.collection.replace_one(
                {"_id": str(newspaper.id)}, db_model.model_dump(by_alias=True)
            )
            if result.modified_count > 0:
                self.logger.info(f"Updated newspaper with ID: {newspaper.id}")
                return newspaper
            else:
                raise ValueError(f"Newspaper with ID {newspaper.id} not found")
        except Exception as e:
            self.logger.error(f"Error updating newspaper {newspaper.id}: {str(e)}")
            raise
