from typing import List, Optional

from injector import inject
from pymongo import UpdateOne

from commons.repository.mongo.optimistic_locking_utils import (
    create_optimistic_locking_update_op, validate_bulk_write_result)
from data_collector_service.models.webpage.webpage_collected_content import \
    WebpageCollectedContent
from data_collector_service.repositories.mongodb.adapters.webpage_collected_content_adapter import \
    WebpageCollectedContentAdapter
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from data_collector_service.repositories.mongodb.models.webpage_collected_content_db_model import \
    WebpageCollectedContentDBModel
from data_collector_service.repositories.webpage_collected_content_repository import \
    WebpageCollectedContentRepository


class MongoDBWebpageCollectedContentRepository(WebpageCollectedContentRepository):
    """MongoDB implementation of the webpage collected content repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.settings = get_mongodb_settings()
        self.collection = mongodb.get_database()[self.settings.WEBPAGE_COLLECTION_NAME]
        # Create unique index on sha for duplicate detection
        self.collection.create_index("sha", unique=True)

    def upsert_webpages(self, webpages: List[WebpageCollectedContent]) -> None:
        """Add or update webpages in the collection."""

        operations = []
        for webpage in webpages:
            db_model = WebpageCollectedContentAdapter.to_db_model(webpage)
            webpage_dict = db_model.model_dump(by_alias=True)

            # Use centralized optimistic locking utility
            operations.append(
                create_optimistic_locking_update_op(
                    filter_query={"id": webpage.id},
                    update_dict=webpage_dict,
                    version=webpage.version,
                )
            )

        if operations:
            result = self.collection.bulk_write(operations)
            validate_bulk_write_result(
                result=result,
                expected_count=len(operations),
                model_name="WebpageCollectedContent",
            )

    def get_webpage_by_id(self, id: str) -> WebpageCollectedContent:
        """Retrieve a webpage by its ID."""
        doc = self.collection.find_one({"id": id})
        if not doc:
            raise ValueError(f"Webpage with ID {id} not found")

        db_model = WebpageCollectedContentDBModel(**doc)
        return WebpageCollectedContentAdapter.from_db_model(db_model)

    def get_webpages_by_ids(self, ids: List[str]) -> List[WebpageCollectedContent]:
        """Retrieve multiple webpages by their IDs."""
        cursor = self.collection.find({"id": {"$in": ids}})
        webpages = []
        for doc in cursor:
            db_model = WebpageCollectedContentDBModel(**doc)
            webpages.append(WebpageCollectedContentAdapter.from_db_model(db_model))
        return webpages

    def filter_existing_webpages(self, shas: List[str]) -> List[str]:
        """Get list of SHA hashes that haven't been added to the collection yet."""
        # Find all webpages that are already in this collection
        cursor = self.collection.find({"sha": {"$in": shas}}, {"sha": 1})
        existing_docs = list(cursor)
        existing_shas = {doc["sha"] for doc in existing_docs}

        print(
            f"[WebpageRepository] Filtered raw content: {len(existing_shas)} already exist globally out of {len(shas)} requested"
        )

        return [sha for sha in shas if sha not in existing_shas]

    def get_webpage_by_sha(self, sha: str) -> Optional[WebpageCollectedContent]:
        """Retrieve a webpage by its SHA hash."""
        doc = self.collection.find_one({"sha": sha})
        if not doc:
            return None
        db_model = WebpageCollectedContentDBModel(**doc)
        return WebpageCollectedContentAdapter.from_db_model(db_model)
