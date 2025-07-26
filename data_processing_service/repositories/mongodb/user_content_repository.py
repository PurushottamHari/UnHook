"""
MongoDB implementation of user content repository.
"""

from typing import List

from pymongo import UpdateOne

from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentSubStatus, ContentType, UserCollectedContent)
from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import \
    CollectedContentAdapter
from data_collector_service.repositories.mongodb.models.collected_content_db_model import \
    CollectedContentDBModel
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel

from ..user_content_repository import UserContentRepository


class MongoDBUserContentRepository(UserContentRepository):
    """MongoDB implementation of user content repository."""

    def __init__(self, database):
        """
        Initialize the repository.

        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collected_content_collection = database.collected_content
        self.generated_content_collection = database.generated_content
        # Ensure unique index on external_id in generated_content collection
        self.generated_content_collection.create_index("external_id", unique=True)

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
        self.collected_content_collection.update_one(
            {"_id": _id}, {"$set": update_dict}
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
            operations.append(UpdateOne({"_id": _id}, {"$set": update_dict}))
        if operations:
            self.collected_content_collection.bulk_write(operations)

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

    def add_generated_content(self, generated_content: GeneratedContent):
        generated_content_db_model = (
            GeneratedContentAdapter.to_generated_content_db_model(
                content=generated_content
            )
        )
        # Insert the generated content into the generated_content_collection
        self.generated_content_collection.insert_one(
            generated_content_db_model.model_dump(by_alias=True)
        )

    def get_generated_content(
        self,
        status: GeneratedContentStatus,
        content_type: ContentType,
    ) -> List[GeneratedContent]:
        """
        Get list of generated content with the given status and content_type.
        Args:
            status: The status of the generated content to filter by
            content_type: The content type to filter by
        Returns:
            List[GeneratedContent]: List of generated content items
        """
        cursor = self.generated_content_collection.find(
            {
                "status": status,
                "content_type": content_type,
            }
        )
        return [
            GeneratedContentAdapter.from_generated_content_db_model(
                GeneratedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def update_generated_content(self, updated_generated_content: GeneratedContent):
        """
        Update a single GeneratedContent item in MongoDB.
        Args:
            updated_generated_content: The GeneratedContent object to update
        """
        db_model = GeneratedContentAdapter.to_generated_content_db_model(
            updated_generated_content
        )
        update_dict = db_model.model_dump(by_alias=True, exclude_unset=True)
        _id = update_dict.pop("_id")
        self.generated_content_collection.update_one(
            {"_id": _id}, {"$set": update_dict}
        )

    def update_generated_content_batch(
        self, updated_generated_content_list: List[GeneratedContent]
    ):
        """
        Update a batch of GeneratedContent items in MongoDB.
        Args:
            updated_generated_content_list: List of GeneratedContent objects to update
        """
        operations = []
        for content in updated_generated_content_list:
            db_model = GeneratedContentAdapter.to_generated_content_db_model(content)
            update_dict = db_model.model_dump(by_alias=True, exclude_unset=True)
            _id = update_dict.pop("_id")
            operations.append(UpdateOne({"_id": _id}, {"$set": update_dict}))
        if operations:
            self.generated_content_collection.bulk_write(operations)

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
                # Update user collected content
                self.collected_content_collection.update_one(
                    {"_id": user_content_id},
                    {"$set": user_content_update_dict},
                    session=session,
                )

                # Update generated content
                self.generated_content_collection.update_one(
                    {"_id": generated_content_id},
                    {"$set": generated_content_update_dict},
                    session=session,
                )
