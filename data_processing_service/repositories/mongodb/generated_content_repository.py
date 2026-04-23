"""
MongoDB implementation of generated content repository.
"""

from typing import Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.user_collected_content import ContentType
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel

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

    def update_generated_content(
        self, updated_generated_content: GeneratedContent
    ) -> None:
        """Update an existing generated content item."""
        db_model = GeneratedContentAdapter.to_generated_content_db_model(
            updated_generated_content
        )
        update_dict = db_model.model_dump(by_alias=True, exclude_unset=True)
        _id = update_dict.pop("_id")
        self.generated_content_collection.update_one(
            {"_id": _id}, {"$set": update_dict}
        )
