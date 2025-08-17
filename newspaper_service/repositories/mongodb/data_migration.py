import os
import sys
from calendar import weekday

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime

import pytz

from data_collector_service.models.user_collected_content import ContentStatus
from newspaper_service.external.user_service import UserServiceClient
from newspaper_service.repositories.mongodb.config.database import MongoDB
from newspaper_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from newspaper_service.repositories.mongodb.generated_content_repository import \
    MongoDBGeneratedContentRepository
from newspaper_service.repositories.mongodb.newspaper_repository import \
    MongoDBNewspaperRepository
from newspaper_service.repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from user_service.models.enums import Weekday


def filter_newspaper_considered_items_by_weekday(newspaper_id: str, for_date: datetime):
    """
    Migration script to fetch a newspaper by ID and date, then filter the considered items
    using weekday logic from create_newspaper_service.py.
    """
    # Initialize repositories
    user_collected_content_repository = MongoDBUserCollectedContentRepository()
    generated_content_repository = MongoDBGeneratedContentRepository()
    newspaper_repository = MongoDBNewspaperRepository(
        user_collected_content_repository=user_collected_content_repository
    )
    user_service_client = UserServiceClient()

    # Get weekday from date (same logic as in create_newspaper_service.py)
    def get_weekday_from_date(date: datetime) -> Weekday:
        """Get the weekday enum from a datetime object."""
        weekday_map = {
            0: Weekday.MONDAY,
            1: Weekday.TUESDAY,
            2: Weekday.WEDNESDAY,
            3: Weekday.THURSDAY,
            4: Weekday.FRIDAY,
            5: Weekday.SATURDAY,
            6: Weekday.SUNDAY,
        }
        # Convert to local timezone if needed and get weekday (0=Monday, 6=Sunday)
        local_date = date.astimezone(pytz.timezone("Asia/Kolkata"))
        weekday_num = local_date.weekday()
        return weekday_map[weekday_num]

    def get_allowed_categories_for_date(user, for_date: datetime):
        """Get categories that should be considered for the given date based on user interests and weekdays."""
        weekday = get_weekday_from_date(for_date)
        allowed_categories = []

        for interest in user.interested:
            if weekday in interest.weekdays:
                allowed_categories.append(interest.category_name)

        return allowed_categories

    try:
        # Fetch the newspaper by ID
        newspaper = newspaper_repository.get_newspaper(newspaper_id)
        if not newspaper:
            print(f"Newspaper with ID {newspaper_id} not found")
            return

        # Fetch user to get interests
        user = user_service_client.get_user(newspaper.user_id)
        if not user:
            print(f"User not found: {newspaper.user_id}")
            return

        # Get allowed categories for the given date
        allowed_categories = get_allowed_categories_for_date(user, for_date)
        weekday = get_weekday_from_date(for_date)
        print(f"Allowed categories for {weekday} on {for_date}: {allowed_categories}")

        # Get considered content items
        considered_items = newspaper.considered_content_list
        print(f"Found {len(considered_items)} considered articles")

        # Get external IDs from considered items
        considered_content_ids = [
            item.user_collected_content_id for item in considered_items
        ]

        # Fetch the actual user collected content to get external IDs
        user_collected_contents = []
        for content_id in considered_content_ids:
            content = user_collected_content_repository.get_content_by_id(content_id)
            if content:
                user_collected_contents.append(content)

        # Get external IDs
        external_ids = [content.external_id for content in user_collected_contents]

        # Filter external IDs by categories using generated content repository
        filtered_external_ids = (
            generated_content_repository.filter_external_ids_by_category(
                external_ids=external_ids,
                categories=allowed_categories,
            )
        )
        print(f"Filtered {len(filtered_external_ids)} external IDs")
        print(f"Filtered external IDs: {filtered_external_ids}")

        # Filter the considered items to only include those with matching external IDs
        filtered_considered_items = []
        non_filtered_content_ids = []

        for item in considered_items:
            # Find the corresponding user collected content
            corresponding_content = next(
                (
                    content
                    for content in user_collected_contents
                    if content.id == item.user_collected_content_id
                ),
                None,
            )
            if (
                corresponding_content
                and corresponding_content.external_id in filtered_external_ids
            ):
                filtered_considered_items.append(item)
            else:
                non_filtered_content_ids.append(item.user_collected_content_id)

        print(f"Filtered {len(filtered_considered_items)} articles")
        print(f"Non-filtered content IDs: {non_filtered_content_ids}")

        # Update non-filtered content to PROCESSED status
        if non_filtered_content_ids:
            update_non_filtered_content_to_processed(non_filtered_content_ids)

        # Update newspaper to remove non-filtered items from considered list
        update_newspaper_considered_list(newspaper_id, filtered_considered_items)

        return filtered_considered_items

    except Exception as e:
        print(f"Error filtering newspaper considered items: {str(e)}")
        raise


def update_non_filtered_content_to_processed(content_ids: list):
    """Update user collected content to PROCESSED status for non-filtered items."""
    try:
        # Get database connection using the newspaper service pattern
        db = MongoDB.get_database()
        settings = get_mongodb_settings()
        collection = db[settings.USER_COLLECTED_CONTENT_COLLECTION_NAME]

        current_timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp()

        # Create new status detail for PROCESSED status
        new_status_detail = {
            "status": ContentStatus.PROCESSED.value,
            "created_at": current_timestamp,
            "reason": "Migration: Content filtered out from newspaper consideration",
        }

        # Update all non-filtered content to PROCESSED status
        update_result = collection.update_many(
            {"_id": {"$in": content_ids}},
            {
                "$set": {
                    "status": ContentStatus.PROCESSED.value,
                    "updated_at": current_timestamp,
                },
                "$push": {"status_details": new_status_detail},
            },
        )

        print(
            f"Updated {update_result.modified_count} user collected content items to PROCESSED status"
        )

    except Exception as e:
        print(f"Error updating non-filtered content to PROCESSED: {str(e)}")
        raise


def update_newspaper_considered_list(
    newspaper_id: str, filtered_considered_items: list
):
    """Update newspaper to only include filtered considered items."""
    try:
        # Get database connection using the newspaper service pattern
        db = MongoDB.get_database()
        settings = get_mongodb_settings()
        collection = db[settings.NEWSPAPER_COLLECTION_NAME]

        current_timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp()

        # Convert filtered considered items to database format
        from newspaper_service.models import ConsideredContent
        from newspaper_service.repositories.mongodb.adapters.newspaper_adapter import \
            NewspaperAdapter

        filtered_considered_db_items = []
        for item in filtered_considered_items:
            db_item = NewspaperAdapter._considered_to_db_model(item)
            filtered_considered_db_items.append(db_item.model_dump())

        # Update the newspaper document
        update_result = collection.update_one(
            {"_id": newspaper_id},
            {
                "$set": {
                    "considered_content_list": filtered_considered_db_items,
                    "updated_at": current_timestamp,
                }
            },
        )

        print(
            f"Updated newspaper {newspaper_id} with {len(filtered_considered_items)} filtered considered items"
        )

    except Exception as e:
        print(f"Error updating newspaper considered list: {str(e)}")
        raise


def process_newspaper_acceptance(newspaper_id: str):
    """
    Migration script to process a newspaper by:
    1. Setting all considered content status to ACCEPTED
    2. Marking user collected content as USED
    3. Updating newspaper read time based on generated content reading times
    """
    # Initialize repositories
    user_collected_content_repository = MongoDBUserCollectedContentRepository()
    generated_content_repository = MongoDBGeneratedContentRepository()
    newspaper_repository = MongoDBNewspaperRepository(
        user_collected_content_repository=user_collected_content_repository
    )

    try:
        # Fetch the newspaper by ID
        newspaper = newspaper_repository.get_newspaper(newspaper_id)
        if not newspaper:
            print(f"Newspaper with ID {newspaper_id} not found")
            return

        print(
            f"Processing newspaper {newspaper_id} with {len(newspaper.considered_content_list)} considered items"
        )

        # Get considered content items
        considered_items = newspaper.considered_content_list
        considered_content_ids = [
            item.user_collected_content_id for item in considered_items
        ]

        # Fetch the actual user collected content to get external IDs
        user_collected_contents = []
        for content_id in considered_content_ids:
            content = user_collected_content_repository.get_content_by_id(content_id)
            if content:
                user_collected_contents.append(content)

        # Get external IDs
        external_ids = [content.external_id for content in user_collected_contents]
        print(f"Found {len(external_ids)} external IDs")

        # Calculate total reading time from generated content
        total_reading_time = 0
        for external_id in external_ids:
            generated_content = generated_content_repository.get_content_by_external_id(
                external_id
            )
            if generated_content and generated_content.reading_time_seconds:
                total_reading_time += generated_content.reading_time_seconds
                print(
                    f"External ID {external_id}: {generated_content.reading_time_seconds} seconds"
                )

        print(f"Total reading time: {total_reading_time} seconds")

        # Update considered content status to ACCEPTED
        update_considered_content_to_accepted(newspaper_id, considered_items)

        # Update user collected content to USED status
        update_user_collected_content_to_used(considered_content_ids)

        # Update newspaper reading time
        update_newspaper_reading_time(newspaper_id, total_reading_time)

        print(f"Successfully processed newspaper {newspaper_id}")
        print(f"- Updated {len(considered_items)} considered items to ACCEPTED")
        print(
            f"- Updated {len(considered_content_ids)} user collected content items to USED"
        )
        print(f"- Updated newspaper reading time to {total_reading_time} seconds")

    except Exception as e:
        print(f"Error processing newspaper acceptance: {str(e)}")
        raise


def update_considered_content_to_accepted(newspaper_id: str, considered_items: list):
    """Update considered content status to ACCEPTED."""
    try:
        # Get database connection using the newspaper service pattern
        db = MongoDB.get_database()
        settings = get_mongodb_settings()
        collection = db[settings.NEWSPAPER_COLLECTION_NAME]

        current_timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp()

        # Convert considered items to database format with ACCEPTED status
        from newspaper_service.models import (ConsideredContent,
                                              ConsideredContentStatus)
        from newspaper_service.repositories.mongodb.adapters.newspaper_adapter import \
            NewspaperAdapter

        accepted_considered_db_items = []
        for item in considered_items:
            # Create new item with ACCEPTED status
            accepted_item = ConsideredContent(
                user_collected_content_id=item.user_collected_content_id,
                considered_content_status=ConsideredContentStatus.ACCEPTED,
            )
            # Set status with reason
            accepted_item.set_status(
                ConsideredContentStatus.ACCEPTED,
                reason="Migration: Content accepted for newspaper",
            )
            # Convert to database format
            db_item = NewspaperAdapter._considered_to_db_model(accepted_item)
            accepted_considered_db_items.append(db_item.model_dump())

        # Update the newspaper document
        update_result = collection.update_one(
            {"_id": newspaper_id},
            {
                "$set": {
                    "considered_content_list": accepted_considered_db_items,
                    "updated_at": current_timestamp,
                }
            },
        )

        print(
            f"Updated newspaper {newspaper_id} with {len(accepted_considered_db_items)} accepted considered items"
        )

    except Exception as e:
        print(f"Error updating considered content to ACCEPTED: {str(e)}")
        raise


def update_user_collected_content_to_used(content_ids: list):
    """Update user collected content to USED status."""
    try:
        # Get database connection using the newspaper service pattern
        db = MongoDB.get_database()
        settings = get_mongodb_settings()
        collection = db[settings.USER_COLLECTED_CONTENT_COLLECTION_NAME]

        current_timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp()

        # Create new status detail for USED status
        new_status_detail = {
            "status": ContentStatus.USED.value,
            "created_at": current_timestamp,
            "reason": "Migration: Content accepted and used in newspaper",
        }

        # Update all content to USED status
        update_result = collection.update_many(
            {"_id": {"$in": content_ids}},
            {
                "$set": {
                    "status": ContentStatus.USED.value,
                    "updated_at": current_timestamp,
                },
                "$push": {"status_details": new_status_detail},
            },
        )

        print(
            f"Updated {update_result.modified_count} user collected content items to USED status"
        )

    except Exception as e:
        print(f"Error updating user collected content to USED: {str(e)}")
        raise


def update_newspaper_reading_time(newspaper_id: str, reading_time_seconds: int):
    """Update newspaper reading time."""
    try:
        # Get database connection using the newspaper service pattern
        db = MongoDB.get_database()
        settings = get_mongodb_settings()
        collection = db[settings.NEWSPAPER_COLLECTION_NAME]

        current_timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp()

        # Update the newspaper document
        update_result = collection.update_one(
            {"_id": newspaper_id},
            {
                "$set": {
                    "reading_time_in_seconds": reading_time_seconds,
                    "updated_at": current_timestamp,
                }
            },
        )

        print(
            f"Updated newspaper {newspaper_id} reading time to {reading_time_seconds} seconds"
        )

    except Exception as e:
        print(f"Error updating newspaper reading time: {str(e)}")
        raise


def update_used_content_to_processed():
    """
    Migration script to update all user collected content with status USED to PROCESSED.
    This migration is useful when content that was previously marked as USED should be
    considered as PROCESSED instead, allowing it to be potentially used again.
    """
    try:
        # Get database connection using the newspaper service pattern
        db = MongoDB.get_database()
        settings = get_mongodb_settings()
        collection = db[settings.USER_COLLECTED_CONTENT_COLLECTION_NAME]

        current_timestamp = datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp()

        # Create new status detail for PROCESSED status
        new_status_detail = {
            "status": ContentStatus.PROCESSED.value,
            "created_at": current_timestamp,
            "reason": "Migration: Content status updated from USED to PROCESSED",
        }

        # Find all documents with USED status
        used_content = collection.find({"status": ContentStatus.USED.value})
        used_content_list = list(used_content)

        if not used_content_list:
            print("No content found with USED status")
            return

        print(f"Found {len(used_content_list)} content items with USED status")

        # Get all IDs of content with USED status
        used_content_ids = [content["_id"] for content in used_content_list]

        # Update all USED content to PROCESSED status
        update_result = collection.update_many(
            {"status": ContentStatus.USED.value},
            {
                "$set": {
                    "status": ContentStatus.PROCESSED.value,
                    "updated_at": current_timestamp,
                },
                "$push": {"status_details": new_status_detail},
            },
        )

        print(
            f"Successfully updated {len(used_content_ids)} user collected content items "
            f"from USED to PROCESSED status"
        )

        # Verify the update
        remaining_used_content = collection.count_documents(
            {"status": ContentStatus.USED.value}
        )
        processed_content_count = collection.count_documents(
            {"status": ContentStatus.PROCESSED.value}
        )

        print(f"Remaining content with USED status: {remaining_used_content}")
        print(f"Total content with PROCESSED status: {processed_content_count}")

    except Exception as e:
        print(f"Error updating USED content to PROCESSED: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage for the migration functions

    # To run the USED to PROCESSED migration:
    update_used_content_to_processed()

    # To process newspaper acceptance:
    # newspaper_id = (
    #     "a9082976-9352-49bb-b643-c845f04fa7d1"  # Replace with actual newspaper ID
    # )
    # process_newspaper_acceptance(newspaper_id)

    # To filter newspaper considered items by weekday:
    # from datetime import datetime
    # import pytz
    # for_date = datetime.now(pytz.timezone("Asia/Kolkata"))
    # filter_newspaper_considered_items_by_weekday(newspaper_id, for_date)
