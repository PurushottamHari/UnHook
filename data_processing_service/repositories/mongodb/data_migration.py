import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime, timezone

from data_collector_service.models.user_collected_content import ContentStatus
from data_collector_service.repositories.mongodb.config.database import \
    MongoDB as CollectorMongoDB
from data_collector_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from data_processing_service.repositories.ephemeral.local.youtube_content_ephemeral_repository import \
    LocalYoutubeContentEphemeralRepository
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel
from data_processing_service.utils.content_utils import calculate_reading_time
from user_service.models import OutputType


def migrate_generated_content_status_details():
    """
    Migration script to fix generated_content.status_details from object to list.
    """
    print("Starting data migration for generated_content.status_details...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    generated_content_collection = db.generated_content

    print(f"Connected to generated_content collection.")

    # Find all documents where status_details is a dict (should be a list)
    documents = list(
        generated_content_collection.find({"status_details": {"$type": "object"}})
    )
    print(f"Found {len(documents)} documents to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        status_details = doc.get("status_details")
        if isinstance(status_details, dict):
            # Convert to single-element list
            new_status_details = [status_details]
            generated_content_collection.update_one(
                {"_id": doc_id}, {"$set": {"status_details": new_status_details}}
            )
            updated_count += 1
            print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_user_collected_content_to_processed():
    """
    Migration script to update user_collected_content status to PROCESSED for records
    that have corresponding generated_content with ARTICLE_GENERATED status.
    """
    print("Starting migration to update user_collected_content to PROCESSED status...")

    # Connect to data processing service MongoDB
    MongoDB.connect_to_database()
    processing_db = MongoDB.get_database()
    generated_content_collection = processing_db.generated_content

    # Connect to data collector service MongoDB
    CollectorMongoDB.connect_to_database()
    collector_db = CollectorMongoDB.get_database()
    collector_settings = get_mongodb_settings()
    user_collected_content_collection = collector_db[collector_settings.COLLECTION_NAME]

    print(
        f"Connected to generated_content and {collector_settings.COLLECTION_NAME} collections."
    )

    # Find all generated_content documents with ARTICLE_GENERATED status
    generated_docs = list(
        generated_content_collection.find(
            {"status": GeneratedContentStatus.ARTICLE_GENERATED}
        )
    )
    print(
        f"Found {len(generated_docs)} generated_content documents with ARTICLE_GENERATED status."
    )

    # Extract external_ids from generated content
    external_ids = [doc["external_id"] for doc in generated_docs]
    print(f"External IDs to process: {external_ids}")

    # Find corresponding user_collected_content records
    user_collected_docs = list(
        user_collected_content_collection.find({"external_id": {"$in": external_ids}})
    )
    print(
        f"Found {len(user_collected_docs)} corresponding user_collected_content records."
    )

    # Update user_collected_content records to PROCESSED status
    updated_count = 0
    current_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

    for doc in user_collected_docs:
        doc_id = doc["_id"]
        external_id = doc["external_id"]

        # Create new status detail for PROCESSED status
        new_status_detail = {
            "status": ContentStatus.PROCESSED,
            "created_at": current_timestamp,
            "reason": "Migration: Article generation completed",
        }

        # Update the document
        update_result = user_collected_content_collection.update_one(
            {"_id": doc_id},
            {
                "$set": {
                    "status": ContentStatus.PROCESSED,
                    "updated_at": current_timestamp,
                },
                "$push": {"status_details": new_status_detail},
            },
        )

        if update_result.modified_count > 0:
            updated_count += 1
            print(
                f"Updated user_collected_content document {doc_id} for external_id {external_id}"
            )

    print(
        f"Migration complete. {updated_count} user_collected_content documents updated to PROCESSED status."
    )

    # Close the connections
    MongoDB.close_database_connection()
    CollectorMongoDB.close_database_connection()
    print("Database connections closed.")


def migrate_user_collected_content_to_subtitle_stored():
    """
    Migration script to update user_collected_content sub_status to SUBTITLES_STORED
    for records that have valid subtitle files stored in the ephemeral repository and user_collected_content with MODERATION_PASSED sub_status.
    """
    print("Starting migration to update user_collected_content to SUBTITLES_STORED...")

    # Connect to data collector service MongoDB
    CollectorMongoDB.connect_to_database()
    collector_db = CollectorMongoDB.get_database()
    collector_settings = get_mongodb_settings()
    user_collected_content_collection = collector_db[collector_settings.COLLECTION_NAME]

    print(f"Connected to {collector_settings.COLLECTION_NAME} collection.")

    # Find all user_collected_content documents with sub_status MODERATION_PASSED
    user_collected_docs = list(
        user_collected_content_collection.find({"sub_status": "MODERATION_PASSED"})
    )
    print(
        f"Found {len(user_collected_docs)} user_collected_content documents with sub_status MODERATION_PASSED."
    )

    # Initialize ephemeral repository
    ephemeral_repository = LocalYoutubeContentEphemeralRepository()

    updated_count = 0
    current_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

    for doc in user_collected_docs:
        doc_id = doc["_id"]
        external_id = doc["external_id"]

        # Check if clean subtitles exist for this external_id
        try:
            subtitle_data = ephemeral_repository.get_all_clean_subtitle_file_data(
                video_id=external_id
            )
            # Check if we have valid clean subtitles (not empty)
            has_valid_subtitles = False
            if subtitle_data.automatic:
                for subtitle_map in subtitle_data.automatic:
                    if subtitle_map.subtitle and subtitle_map.subtitle.strip():
                        has_valid_subtitles = True
                        break
            if not has_valid_subtitles and subtitle_data.manual:
                for subtitle_map in subtitle_data.manual:
                    if subtitle_map.subtitle and subtitle_map.subtitle.strip():
                        has_valid_subtitles = True
                        break
            if has_valid_subtitles:
                # Update user_collected_content
                new_sub_status_detail = {
                    "sub_status": "SUBTITLES_STORED",
                    "created_at": current_timestamp,
                    "reason": "Migration: Valid subtitle files found",
                }
                # user_collected_content_collection.update_one(
                #     {"_id": doc_id},
                #     {
                #         "$set": {
                #             "sub_status": "SUBTITLES_STORED",
                #             "updated_at": current_timestamp,
                #         },
                #         "$push": {"sub_status_details": new_sub_status_detail},
                #     },
                # )
                updated_count += 1
                print(f"Updated user_collected_content for external_id {external_id}")
            else:
                print(
                    f"No valid clean subtitles found for external_id {external_id}, skipping."
                )
        except Exception as e:
            print(f"Error checking subtitles for external_id {external_id}: {str(e)}")
            continue

    print(
        f"Migration complete. {updated_count} user_collected_content records updated to SUBTITLES_STORED."
    )

    # Close the connection
    CollectorMongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_fix_missing_subtitles_stored_sub_status_details():
    """
    Migration script to fix missing sub_status_details entries for records
    that have sub_status as "SUBTITLES_STORED" but only have one entry in sub_status_details.
    """
    print("Starting migration to fix missing SUBTITLES_STORED sub_status_details...")

    # Connect to data collector service MongoDB
    CollectorMongoDB.connect_to_database()
    collector_db = CollectorMongoDB.get_database()
    collector_settings = get_mongodb_settings()
    user_collected_content_collection = collector_db[collector_settings.COLLECTION_NAME]

    print(f"Connected to {collector_settings.COLLECTION_NAME} collection.")

    # Find all user_collected_content documents with sub_status SUBTITLES_STORED
    # that have only one entry in sub_status_details
    user_collected_docs = list(
        user_collected_content_collection.find(
            {"sub_status": "SUBTITLES_STORED", "sub_status_details": {"$size": 1}}
        )
    )
    print(
        f"Found {len(user_collected_docs)} user_collected_content documents with sub_status SUBTITLES_STORED and only one sub_status_details entry."
    )

    updated_count = 0
    current_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

    for doc in user_collected_docs:
        doc_id = doc["_id"]
        external_id = doc["external_id"]
        sub_status_details = doc.get("sub_status_details", [])

        # Check if the existing entry is for SUBTITLES_STORED
        if len(sub_status_details) == 1:
            existing_detail = sub_status_details[0]
            if existing_detail.get("sub_status") == "SUBTITLES_STORED":
                print(
                    f"Document {doc_id} already has SUBTITLES_STORED in sub_status_details, skipping."
                )
                continue

        # Add the missing SUBTITLES_STORED entry
        new_sub_status_detail = {
            "sub_status": "SUBTITLES_STORED",
            "created_at": current_timestamp,
            "reason": "Migration: Subtitles stored status added",
        }

        # Update the document
        update_result = user_collected_content_collection.update_one(
            {"_id": doc_id},
            {
                "$push": {"sub_status_details": new_sub_status_detail},
                "$set": {"updated_at": current_timestamp},
            },
        )

        if update_result.modified_count > 0:
            updated_count += 1
            print(
                f"Updated user_collected_content document {doc_id} for external_id {external_id}"
            )

    print(
        f"Migration complete. {updated_count} user_collected_content documents updated with missing SUBTITLES_STORED sub_status_details."
    )

    # Close the connection
    CollectorMongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_fix_wrongfully_rejected_content():
    """
    Migration script to fix wrongfully rejected user_collected_content records.
    Updates status to PROCESSING and sub_status to MODERATION_PASSED for specific external_ids.
    """
    print("Starting migration to fix wrongfully rejected user_collected_content...")

    # External IDs that were wrongfully rejected
    wrongfully_rejected_external_ids = [
        "7NCC61U7AH0",
        "t8kAs0K3t4Y",
        "u6XQFqQahgU",
        "xIC9sCRSwww",
    ]

    # Connect to data collector service MongoDB
    CollectorMongoDB.connect_to_database()
    collector_db = CollectorMongoDB.get_database()
    collector_settings = get_mongodb_settings()
    user_collected_content_collection = collector_db[collector_settings.COLLECTION_NAME]

    print(f"Connected to {collector_settings.COLLECTION_NAME} collection.")

    # Find all user_collected_content documents with the specified external_ids
    user_collected_docs = list(
        user_collected_content_collection.find(
            {"external_id": {"$in": wrongfully_rejected_external_ids}}
        )
    )
    print(f"Found {len(user_collected_docs)} user_collected_content documents to fix.")

    updated_count = 0
    current_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

    for doc in user_collected_docs:
        doc_id = doc["_id"]
        external_id = doc["external_id"]

        # Create new status detail for PROCESSING status
        new_status_detail = {
            "status": ContentStatus.PROCESSING,
            "created_at": current_timestamp,
            "reason": "Migration: Fixing wrongfully rejected content",
        }

        # Create new sub_status detail for MODERATION_PASSED status
        new_sub_status_detail = {
            "sub_status": "MODERATION_PASSED",
            "created_at": current_timestamp,
            "reason": "Migration: Content was wrongfully rejected, now approved",
        }

        # Update the document
        update_result = user_collected_content_collection.update_one(
            {"_id": doc_id},
            {
                "$set": {
                    "status": ContentStatus.PROCESSING,
                    "sub_status": "MODERATION_PASSED",
                    "updated_at": current_timestamp,
                },
                "$push": {
                    "status_details": new_status_detail,
                    "sub_status_details": new_sub_status_detail,
                },
            },
        )

        if update_result.modified_count > 0:
            updated_count += 1
            print(
                f"Updated user_collected_content document {doc_id} for external_id {external_id}"
            )

    print(
        f"Migration complete. {updated_count} user_collected_content documents updated."
    )

    # Close the connection
    CollectorMongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_calculate_reading_time_for_generated_content():
    """
    Migration script to calculate and set reading_time_seconds for all generated_content
    with ARTICLE_GENERATED status. Fetches the article content (MEDIUM or LONG) and
    calculates reading time using the calculate_reading_time utility.
    """
    print("Starting migration to calculate reading time for generated content...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    generated_content_collection = db.generated_content

    print(f"Connected to generated_content collection.")

    # Find all generated_content documents with ARTICLE_GENERATED status
    generated_docs = list(
        generated_content_collection.find(
            {"status": GeneratedContentStatus.ARTICLE_GENERATED}
        )
    )
    print(
        f"Found {len(generated_docs)} generated_content documents with ARTICLE_GENERATED status."
    )

    updated_count = 0
    current_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()

    for doc in generated_docs:
        doc_id = doc["_id"]
        external_id = doc["external_id"]
        generated = doc.get("generated", {})

        # Try to get article content from MEDIUM or LONG output types
        article_content = ""
        if OutputType.MEDIUM in generated:
            article_content = generated[OutputType.MEDIUM].get("string", "")
        elif OutputType.LONG in generated:
            article_content = generated[OutputType.LONG].get("string", "")

        if not article_content:
            print(
                f"No article content found for document {doc_id} (external_id: {external_id}), skipping."
            )
            continue

        # Calculate reading time using the utility function
        reading_time_seconds = calculate_reading_time(article_content)

        print(
            f"Document {doc_id} (external_id: {external_id}): {reading_time_seconds} seconds reading time"
        )

        # Update the document with reading time and updated timestamp
        update_result = generated_content_collection.update_one(
            {"_id": doc_id},
            {
                "$set": {
                    "reading_time_seconds": reading_time_seconds,
                    "updated_at": current_timestamp,
                }
            },
        )

        if update_result.modified_count > 0:
            updated_count += 1
            print(
                f"Updated document {doc_id} with reading time: {reading_time_seconds} seconds"
            )
        else:
            print(f"No changes made to document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated with reading time.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


if __name__ == "__main__":
    migrate_calculate_reading_time_for_generated_content()
