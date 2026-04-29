"""
MongoDB implementation of generated content repository.
"""

from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel
from newspaper_service.repositories.generated_content_repository import \
    GeneratedContentRepository
from newspaper_service.repositories.mongodb.config.database import MongoDB
from user_service.models.enums import CategoryName


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

    def filter_external_ids_by_criteria(
        self,
        external_ids: List[str],
        categories: List[CategoryName],
        youtube_channels: List[str],
    ) -> List[str]:
        """
        Filter external IDs by categories and channels, returning only those that match
        the criteria and have ARTICLE_GENERATED status.

        NOTE: Currently channel filtering is expected to be handled partially at the
        service layer if they are not stored in GeneratedContent collection.
        This implementation filters by categories.
        """
        if not external_ids:
            return []

        if not categories:
            # If no categories are provided, we can't filter by them here
            return []

        # Convert category enums to string values
        category_values = [cat.value for cat in categories]

        # Efficient query to get only external_ids with matching categories
        cursor = self.generated_content_collection.find(
            {
                "external_id": {"$in": external_ids},
                "status": GeneratedContentStatus.ARTICLE_GENERATED,
                "category.category": {"$in": category_values},
            },
            {"external_id": 1, "_id": 0},  # Only return external_id field
        )

        # Extract external_ids from cursor
        matching_external_ids = [doc["external_id"] for doc in cursor]

        return matching_external_ids

    def get_content_by_id(self, content_id: str) -> GeneratedContent:
        """
        Fetch a single GeneratedContent object by MongoDB _id.

        Args:
            content_id: MongoDB _id to fetch

        Returns:
            GeneratedContent: Generated content object or None if not found
        """
        doc = self.generated_content_collection.find_one({"_id": content_id})

        if not doc:
            return None

        return GeneratedContentAdapter.from_generated_content_db_model(
            GeneratedContentDBModel(**doc)
        )

    def get_content_by_external_id(self, external_id: str) -> GeneratedContent:
        """
        Fetch a single GeneratedContent object by external_id.

        Args:
            external_id: External ID to fetch

        Returns:
            GeneratedContent: Generated content object or None if not found
        """
        doc = self.generated_content_collection.find_one({"external_id": external_id})

        if not doc:
            return None

        return GeneratedContentAdapter.from_generated_content_db_model(
            GeneratedContentDBModel(**doc)
        )

    def get_reading_times_by_external_ids(self, external_ids: List[str]) -> dict:
        """
        Fetch reading times for multiple external IDs efficiently.

        Args:
            external_ids: List of external IDs to fetch reading times for

        Returns:
            dict: Dictionary mapping external_id to reading_time_seconds
        """
        if not external_ids:
            return {}

        cursor = self.generated_content_collection.find(
            {"external_id": {"$in": external_ids}},
            {"external_id": 1, "reading_time_seconds": 1, "_id": 0},
        )

        reading_times = {}
        for doc in cursor:
            reading_times[doc["external_id"]] = doc.get("reading_time_seconds", 0)

        return reading_times

    def get_contents_by_external_ids(
        self, external_ids: List[str]
    ) -> List[GeneratedContent]:
        """
        Fetch multiple GeneratedContent objects by external_ids.

        Args:
            external_ids: List of external IDs to fetch

        Returns:
            List[GeneratedContent]: List of generated content objects with ARTICLE_GENERATED status
        """
        if not external_ids:
            return []

        cursor = self.generated_content_collection.find(
            {"external_id": {"$in": external_ids}}
        )

        contents = []
        for doc in cursor:
            db_model = GeneratedContentDBModel(**doc)
            contents.append(
                GeneratedContentAdapter.from_generated_content_db_model(db_model)
            )

        return contents
