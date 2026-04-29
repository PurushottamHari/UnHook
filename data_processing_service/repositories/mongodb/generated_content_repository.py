"""
MongoDB implementation of generated content repository.
"""

import logging
from typing import List, Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentType)
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel
from data_processing_service.repositories.mongodb.utils.optimistic_locking import \
    create_optimistic_locking_update_op

from ..generated_content_repository import GeneratedContentRepository


@injectable()
class MongoDBGeneratedContentRepository(GeneratedContentRepository):
    """MongoDB implementation of generated content repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        """
        Initialize the repository.

        Args:
            mongodb: MongoDB connection manager
        """
        self.database = mongodb.get_database()
        self.generated_content_collection = self.database.generated_content
        self.collected_content_collection = self.database.collected_content
        self.logger = logging.getLogger(__name__)
        # Ensure unique index on external_id in generated_content collection
        self.generated_content_collection.create_index("external_id", unique=True)

    def add_generated_content(self, generated_content: GeneratedContent) -> None:
        """Add a new generated content item."""
        generated_content_db_model = (
            GeneratedContentAdapter.to_generated_content_db_model(
                content=generated_content
            )
        )
        self.generated_content_collection.insert_one(
            generated_content_db_model.model_dump(by_alias=True)
        )

    def get_generated_content_by_external_id(
        self, external_id: str, content_type: ContentType
    ) -> Optional[GeneratedContent]:
        """Get generated content by its external ID and content type."""
        doc = self.generated_content_collection.find_one(
            {"external_id": external_id, "content_type": content_type}
        )
        if not doc:
            return None
        return GeneratedContentAdapter.from_generated_content_db_model(
            GeneratedContentDBModel(**doc)
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

    def get_generated_content_by_ids(
        self,
        content_ids: List[str],
    ) -> List[GeneratedContent]:
        """
        Get list of generated content with the given IDs.
        Args:
            content_ids: The IDs of the generated content to filter by
        Returns:
            List[GeneratedContent]: List of generated content items
        """
        cursor = self.generated_content_collection.find({"_id": {"$in": content_ids}})
        return [
            GeneratedContentAdapter.from_generated_content_db_model(
                GeneratedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def get_generated_content_by_user_collected_content_status(
        self,
        user_id: str,
        status: GeneratedContentStatus,
        content_type: ContentType,
        user_collected_content_status: ContentStatus,
    ) -> List[GeneratedContent]:
        """
        Get list of generated content with the given status and content_type,
        filtered by the status of the associated user collected content for a specific user.
        """
        pipeline = [
            {
                "$match": {
                    "status": status,
                    "content_type": content_type,
                }
            },
            {
                "$lookup": {
                    "from": "collected_content",
                    "localField": "external_id",
                    "foreignField": "external_id",
                    "as": "collected_docs",
                }
            },
            {
                "$match": {
                    "collected_docs": {
                        "$elemMatch": {
                            "user_id": str(user_id),
                            "status": user_collected_content_status,
                        }
                    }
                }
            },
            {"$project": {"collected_docs": 0}},
        ]

        cursor = self.generated_content_collection.aggregate(pipeline)

        return [
            GeneratedContentAdapter.from_generated_content_db_model(
                GeneratedContentDBModel(**doc)
            )
            for doc in cursor
        ]

    def update_generated_content(
        self, updated_generated_content: GeneratedContent
    ) -> None:
        """Update an existing generated content item."""
        db_model = GeneratedContentAdapter.to_generated_content_db_model(
            updated_generated_content
        )
        update_dict = db_model.model_dump(by_alias=True, exclude_unset=True)
        _id = update_dict.pop("_id")

        # Use the optimistic locking utility
        op = create_optimistic_locking_update_op(
            filter_query={"_id": _id},
            update_dict=update_dict,
            version=updated_generated_content.version,
        )

        result = self.generated_content_collection.bulk_write([op])

        if result.matched_count == 0 and updated_generated_content.version > 1:
            raise ValueError(
                f"Optimistic lock failure for GeneratedContent with id {_id}. "
                f"Expected version {updated_generated_content.version - 1} not found."
            )

    def update_generated_content_batch(
        self, updated_generated_content_list: List[GeneratedContent]
    ) -> None:
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
            # Use the optimistic locking utility
            operations.append(
                create_optimistic_locking_update_op(
                    filter_query={"_id": _id},
                    update_dict=update_dict,
                    version=content.version,
                )
            )
        if operations:
            result = self.generated_content_collection.bulk_write(operations)
            if result.matched_count < len(operations):
                # Only check if versions are > 1
                if any(c.version > 1 for c in updated_generated_content_list):
                    self.logger.warning(
                        f"Optimistic lock failure detected in batch update. "
                        f"Matched {result.matched_count} out of {len(operations)}."
                    )
