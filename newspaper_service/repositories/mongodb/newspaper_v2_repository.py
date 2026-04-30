import logging
from datetime import datetime, timezone
from typing import Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable

from ...models import NewspaperV2
from ..newspaper_v2_repository import NewspaperV2Repository
from .adapters.newspaper_v2_adapter import NewspaperV2Adapter
from .config.database import MongoDB
from .config.settings import get_mongodb_settings
from .models.newspaper_v2_db_model import NewspaperV2DBModel
from .utils.optimistic_locking import create_optimistic_locking_update_op


@injectable()
class MongoDBNewspaperV2Repository(NewspaperV2Repository):
    """MongoDB implementation of NewspaperV2 repository with optimistic locking."""

    @inject
    def __init__(self):
        self.settings = get_mongodb_settings()
        self.database = MongoDB.get_database()
        self.collection = self.database[self.settings.NEWSPAPER_COLLECTION_NAME]
        self.logger = logging.getLogger(__name__)

    def upsert(self, newspaper: NewspaperV2) -> NewspaperV2:
        """Upsert a NewspaperV2 instance using optimistic locking."""
        try:
            # Prepare update document (excluding _id and version which is handled by utility)
            db_model = NewspaperV2Adapter.to_db_model(newspaper)
            update_data = db_model.model_dump(by_alias=True)

            newspaper_id = update_data.pop("_id")

            # Increment version for the next save
            current_version = newspaper.version
            next_version = current_version + 1
            update_data["version"] = next_version

            # Create optimistic locking update operation
            update_op = create_optimistic_locking_update_op(
                filter_query={"_id": newspaper_id},
                update_dict=update_data,
                version=next_version,
                id_for_insert=newspaper_id,
            )

            # Execute update
            result = self.collection.update_one(
                filter=update_op._filter,
                update=update_op._update,
                upsert=update_op._upsert,
            )

            if result.matched_count == 0 and result.upserted_id is None:
                self.logger.error(
                    f"Optimistic lock failure for NewspaperV2 {newspaper_id}. Version: {current_version}"
                )
                raise RuntimeError(
                    f"Optimistic lock failure for NewspaperV2 {newspaper_id}"
                )

            # Update domain model version
            newspaper.version = next_version

            self.logger.info(
                f"Upserted NewspaperV2 with ID: {newspaper_id}, New Version: {next_version}"
            )
            return newspaper
        except Exception as e:
            self.logger.error(f"Error upserting NewspaperV2: {str(e)}")
            raise

    def get_by_id(self, newspaper_id: str) -> Optional[NewspaperV2]:
        """Get a single NewspaperV2 instance by ID."""
        doc = self.collection.find_one({"_id": newspaper_id})
        if doc:
            db_model = NewspaperV2DBModel(**doc)
            return NewspaperV2Adapter.to_internal_model(db_model)
        return None

    def get_by_user_and_date(
        self, user_id: str, for_date: datetime
    ) -> Optional[NewspaperV2]:
        """Get a NewspaperV2 instance for a specific user and date."""
        try:
            if for_date.tzinfo is None:
                for_date = for_date.replace(tzinfo=timezone.utc)

            start_of_day = for_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = for_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            start_timestamp = start_of_day.astimezone(timezone.utc).timestamp()
            end_timestamp = end_of_day.astimezone(timezone.utc).timestamp()

            document = self.collection.find_one(
                {
                    "user_id": user_id,
                    "created_at": {"$gte": start_timestamp, "$lte": end_timestamp},
                }
            )

            if document:
                db_model = NewspaperV2DBModel(**document)
                return NewspaperV2Adapter.to_internal_model(db_model)
            return None
        except Exception as e:
            self.logger.error(f"Error getting NewspaperV2 by user and date: {str(e)}")
            raise
