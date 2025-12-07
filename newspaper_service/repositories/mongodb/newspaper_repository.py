"""
MongoDB implementation of newspaper repository.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from data_collector_service.models.user_collected_content import \
    UserCollectedContent

from ...models import Newspaper
from ..newspaper_repository import NewspaperRepository
from ..user_collected_content_repository import UserCollectedContentRepository
from .adapters.newspaper_adapter import NewspaperAdapter
from .config.database import MongoDB
from .config.settings import get_mongodb_settings
from .models.newspaper_db_model import NewspaperDBModel


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

    def get_newspaper(self, newspaper_id: str) -> Optional[Newspaper]:
        """Get a newspaper by ID."""
        try:
            document = self.collection.find_one({"_id": newspaper_id})
            if document:

                db_model = NewspaperDBModel(**document)
                return NewspaperAdapter.to_internal_model(db_model)
            return None
        except Exception as e:
            self.logger.error(f"Error getting newspaper {newspaper_id}: {str(e)}")
            raise

    def get_newspaper_by_user_and_date(
        self, user_id: str, for_date: datetime
    ) -> Optional[Newspaper]:
        """Get a newspaper for a specific user and date."""
        try:
            # Convert date to start and end of day for comparison
            # Ensure timezone-aware datetime for proper timestamp conversion
            if for_date.tzinfo is None:
                for_date = for_date.replace(tzinfo=timezone.utc)

            start_of_day = for_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = for_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            # Convert datetime objects to timestamps (floats) for MongoDB query
            # since created_at is stored as UTC epoch seconds in the database
            start_timestamp = start_of_day.astimezone(timezone.utc).timestamp()
            end_timestamp = end_of_day.astimezone(timezone.utc).timestamp()

            document = self.collection.find_one(
                {
                    "user_id": user_id,
                    "created_at": {"$gte": start_timestamp, "$lte": end_timestamp},
                }
            )

            if document:
                db_model = NewspaperDBModel(**document)
                return NewspaperAdapter.to_internal_model(db_model)
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting newspaper for user {user_id} on {for_date}: {str(e)}"
            )
            raise

    def upsert_newspaper(self, newspaper: Newspaper) -> Newspaper:
        """Create or update newspaper with all its associated content."""
        try:
            db_model = NewspaperAdapter.to_db_model(newspaper)
            newspaper_doc = db_model.model_dump(by_alias=True)

            # Use a MongoDB transaction to atomically upsert the newspaper
            client = self.database.client
            with client.start_session() as session:
                with session.start_transaction():
                    # Check if newspaper exists
                    existing_doc = self.collection.find_one(
                        {"_id": newspaper.id}, session=session
                    )

                    if existing_doc:
                        # Update existing newspaper
                        newspaper_update = newspaper_doc.copy()
                        if "_id" in newspaper_update:
                            del newspaper_update["_id"]

                        update_result = self.collection.update_one(
                            {"_id": newspaper.id},
                            {"$set": newspaper_update},
                            session=session,
                        )
                        self.logger.info(
                            f"Updated existing newspaper with ID: {newspaper.id}"
                        )
                    else:
                        # Create new newspaper
                        insert_result = self.collection.insert_one(
                            newspaper_doc, session=session
                        )
                        self.logger.info(
                            f"Created new newspaper with ID: {newspaper.id}"
                        )

            return newspaper
        except Exception as e:
            self.logger.error(f"Error upserting newspaper: {str(e)}")
            raise

    def list_newspapers_by_user(
        self,
        user_id: str,
        for_date: Optional[datetime] = None,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> List[Newspaper]:
        """
        List newspapers for a user with pagination, optionally filtered by date.

        Args:
            user_id: User ID to filter newspapers
            for_date: Optional date to filter newspapers (within that day)
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return

        Returns:
            List of Newspaper objects sorted by id descending
        """
        try:
            # Build query filter
            query_filter = {"user_id": user_id}

            # Add date filter if provided
            if for_date:
                # Ensure timezone-aware datetime for proper timestamp conversion
                if for_date.tzinfo is None:
                    for_date = for_date.replace(tzinfo=timezone.utc)

                start_of_day = for_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_of_day = for_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )

                # Convert datetime objects to timestamps (floats) for MongoDB query
                start_timestamp = start_of_day.astimezone(timezone.utc).timestamp()
                end_timestamp = end_of_day.astimezone(timezone.utc).timestamp()

                query_filter["created_at"] = {
                    "$gte": start_timestamp,
                    "$lte": end_timestamp,
                }

            # Build cursor query if starting_after is provided
            if starting_after:
                # For cursor-based pagination with descending sort by _id,
                # we need to find documents with _id less than starting_after
                query_filter["_id"] = {"$lt": starting_after}

            # Query with sort by _id descending and limit
            cursor = (
                self.collection.find(query_filter)
                .sort("_id", -1)  # Sort by id descending
                .limit(page_limit)
            )

            documents = list(cursor)

            # Convert documents to Newspaper objects
            newspapers = []
            for document in documents:
                db_model = NewspaperDBModel(**document)
                newspaper = NewspaperAdapter.to_internal_model(db_model)
                newspapers.append(newspaper)

            return newspapers
        except Exception as e:
            self.logger.error(f"Error listing newspapers for user {user_id}: {str(e)}")
            raise
