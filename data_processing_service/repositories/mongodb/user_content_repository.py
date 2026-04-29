"""
MongoDB implementation of user content repository.
"""

import logging
from typing import List, Optional

from injector import inject
from pymongo import UpdateOne

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentSubStatus, ContentType, UserCollectedContent)
from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import \
    CollectedContentAdapter
from data_collector_service.repositories.mongodb.models.collected_content_db_model import \
    CollectedContentDBModel
from data_processing_service.models.generated_content import GeneratedContent
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.utils.optimistic_locking import \
    create_optimistic_locking_update_op

from ..user_content_repository import UserContentRepository


@injectable()
class MongoDBUserContentRepository(UserContentRepository):
    """MongoDB implementation of user content repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        """
        Initialize the repository.

        Args:
            mongodb: MongoDB connection manager
        """
        self.database = mongodb.get_database()
        self.collected_content_collection = self.database.collected_content
        self.generated_content_collection = self.database.generated_content
        # Ensure unique index on external_id in generated_content collection
        self.generated_content_collection.create_index("external_id", unique=True)
        self.logger = logging.getLogger(__name__)

    def get_unprocessed_content_for_user(
        self, user_id: str
    ) -> List[UserCollectedContent]:
        """
        Get list of unprocessed content for a user.

        Args:
            user_id: The ID of the user

        Returns:
            List[UserCollectedContent]: List of unprocessed content items
        """
        cursor = self.collected_content_collection.find(
            {"user_id": str(user_id), "status": ContentStatus.COLLECTED}
        )

        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_user_collected_content_by_id(
        self, user_id: str, content_id: str
    ) -> Optional[UserCollectedContent]:
        """
        Get a single user collected content item by its ID.
        Args:
            user_id: The ID of the user
            content_id: The ID of the content item
        Returns:
            Optional[UserCollectedContent]: The content item or None if not found
        """
        doc = self.collected_content_collection.find_one(
            {"_id": content_id, "user_id": str(user_id)}
        )
        if not doc:
            return None

        return CollectedContentAdapter.to_user_collected_content(
            CollectedContentDBModel(**doc)
        )

    def update_user_collected_content(
        self, updated_user_collected_content: UserCollectedContent
    ):
        """
        Update a single UserCollectedContent item in MongoDB.
        Args:
            updated_user_collected_content: The UserCollectedContent object to update
        """
        db_model = CollectedContentAdapter.to_collected_content_db_model(
            updated_user_collected_content
        )
        update_dict = db_model.dict(by_alias=True, exclude_unset=True)
        # Mongodb does not allow _id to be passed even if same
        _id = update_dict.pop("_id")

        # Use the optimistic locking utility
        op = create_optimistic_locking_update_op(
            filter_query={"_id": _id},
            update_dict=update_dict,
            version=updated_user_collected_content.version,
        )

        result = self.collected_content_collection.bulk_write([op])

        if result.matched_count == 0 and updated_user_collected_content.version > 1:
            raise ValueError(
                f"Optimistic lock failure for UserCollectedContent with id {_id}. "
                f"Expected version {updated_user_collected_content.version - 1} not found."
            )

    def update_user_collected_content_batch(
        self, updated_user_collected_content_list: List[UserCollectedContent]
    ):
        """
        Update a batch of UserCollectedContent items in MongoDB.
        Args:
            updated_user_collected_content_list: List of UserCollectedContent objects to update
        """
        operations = []
        for content in updated_user_collected_content_list:
            db_model = CollectedContentAdapter.to_collected_content_db_model(content)
            update_dict = db_model.dict(by_alias=True, exclude_unset=True)
            # Mongodb does not allow _id to be passed even if same
            _id = update_dict.pop("_id")
            # Use the optimistic locking utility
            operations.append(
                create_optimistic_locking_update_op(
                    filter_query={"_id": _id},
                    update_dict=update_dict,
                    version=content.version,
                )
            )
        if operations:
            result = self.collected_content_collection.bulk_write(operations)
            if result.matched_count < len(operations):
                # This check is slightly loose as it doesn't tell which one failed,
                # but it ensures we know if something went wrong.
                # Only check if versions are > 1
                if any(c.version > 1 for c in updated_user_collected_content_list):
                    self.logger.warning(
                        f"Optimistic lock failure detected in batch update. "
                        f"Matched {result.matched_count} out of {len(operations)}."
                    )

    def get_user_collected_content(
        self,
        user_id: str,
        status: ContentStatus,
        sub_status: ContentSubStatus,
        content_type: ContentType,
    ) -> List[UserCollectedContent]:
        """
        Get list of content for a user based on the filters
            user_id: The ID of the user

        Returns:
            List[UserCollectedContent]: List of content items in processing status with moderation passed
        """
        cursor = self.collected_content_collection.find(
            {
                "user_id": str(user_id),
                "status": status,
                "sub_status": sub_status,
                "content_type": content_type,
            }
        )

        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_user_collected_content_without_generated_content(
        self,
        user_id: str,
        status: ContentStatus,
        sub_status: ContentSubStatus,
        content_type: ContentType,
    ) -> List[UserCollectedContent]:
        """
        Get list of user collected content for a user with the given status, sub_status, and content_type,
        where there is no generated content with the same external_id and content_type.
        """
        # Find all external_ids in generated_content_collection for this content_type
        generated_external_ids = set(
            doc["external_id"]
            for doc in self.generated_content_collection.find(
                {"content_type": content_type}, {"external_id": 1}
            )
        )
        # Query collected_content_collection for items not in generated_external_ids
        query = {
            "user_id": str(user_id),
            "status": status,
            "sub_status": sub_status,
            "content_type": content_type,
        }
        if generated_external_ids:
            query["external_id"] = {"$nin": list(generated_external_ids)}
        cursor = self.collected_content_collection.find(query)
        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_user_collected_content_by_external_ids(
        self, external_ids: List[str]
    ) -> List[UserCollectedContent]:
        """
        Fetch UserCollectedContent objects for a list of external_ids.
        Returns a list of UserCollectedContent.
        """
        cursor = self.collected_content_collection.find(
            {
                "external_id": {"$in": external_ids},
            }
        )
        return [
            CollectedContentAdapter.to_user_collected_content(
                CollectedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def update_user_collected_content_and_generated_content(
        self,
        user_collected_content: UserCollectedContent,
        generated_content: GeneratedContent,
    ):
        """
        Update user collected content and generated content in one shot.
        """
        # Convert to DB models
        user_collected_content_db_model = (
            CollectedContentAdapter.to_collected_content_db_model(
                user_collected_content
            )
        )
        generated_content_db_model = (
            GeneratedContentAdapter.to_generated_content_db_model(generated_content)
        )

        # Prepare update dictionaries
        user_content_update_dict = user_collected_content_db_model.dict(
            by_alias=True, exclude_unset=True
        )
        generated_content_update_dict = generated_content_db_model.model_dump(
            by_alias=True, exclude_unset=True
        )

        # Remove _id fields as MongoDB doesn't allow them in updates
        user_content_id = user_content_update_dict.pop("_id")
        generated_content_id = generated_content_update_dict.pop("_id")

        # Execute both updates in a single transaction
        with self.database.client.start_session() as session:
            with session.start_transaction():
                # Update user collected content with optimistic locking
                user_content_query = {"_id": user_content_id}
                if user_collected_content.version > 1:
                    user_content_query["version"] = user_collected_content.version - 1

                result_user = self.collected_content_collection.update_one(
                    user_content_query,
                    {"$set": user_content_update_dict},
                    session=session,
                )

                # Update generated content with optimistic locking
                generated_content_query = {"_id": generated_content_id}
                if generated_content.version > 1:
                    generated_content_query["version"] = generated_content.version - 1

                result_gen = self.generated_content_collection.update_one(
                    generated_content_query,
                    {"$set": generated_content_update_dict},
                    session=session,
                )

                if (
                    result_user.matched_count == 0
                    and user_collected_content.version > 1
                ) or (result_gen.matched_count == 0 and generated_content.version > 1):
                    # The transaction will automatically rollback when an exception is raised
                    raise ValueError(
                        "Optimistic lock failure during transactional update of UserCollectedContent and GeneratedContent."
                    )
