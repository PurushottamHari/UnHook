import os
import sys
from datetime import datetime

from pymongo import MongoClient

from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import \
    CollectedContentAdapter

# Add the project root to the Python path
# This is a bit of a hack, a more robust solution would be to have a proper package structure
# or use a script runner that sets the PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_collector_service.collectors.youtube.tools.youtube_external_tool import \
    YouTubeExternalTool
from data_collector_service.repositories.mongodb.adapters.youtube_video_details_adapter import \
    YouTubeVideoDetailsAdapter
from data_collector_service.repositories.mongodb.config.database import MongoDB
from data_collector_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from data_collector_service.repositories.mongodb.models.youtube_video_details import \
    YouTubeVideoDetailsDB


def migrate_timestamps():
    """
    Migration script to update created_at and updated_at fields from string timestamps
    to epoch timestamps in the UserCollectedContent collection.
    """
    print("Starting data migration...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find all documents in the collection
    documents = list(collection.find({}))
    print(f"Found {len(documents)} documents to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        updates = {}

        # Check and update created_at
        if "created_at" in doc and isinstance(doc["created_at"], str):
            try:
                created_at_str = doc["created_at"]
                if created_at_str.endswith("Z"):
                    created_at_str = created_at_str[:-1]
                dt_obj = datetime.fromisoformat(created_at_str)
                updates["created_at"] = dt_obj.timestamp()
            except ValueError:
                print(
                    f"Could not parse created_at for doc {doc_id}: {doc['created_at']}"
                )
                continue

        # Check and update updated_at
        if "updated_at" in doc and isinstance(doc["updated_at"], str):
            try:
                dt_obj = CollectedContentAdapter._convert_iso_to_datetime(
                    doc["updated_at"]
                )
                updates["updated_at"] = dt_obj.timestamp()
            except ValueError:
                print(
                    f"Could not parse updated_at for doc {doc_id}: {doc['updated_at']}"
                )
                continue

        if updates:
            # collection.update_one({'_id': doc_id}, {'$set': updates})
            print("updated one....")
            updated_count += 1
            # print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_data_structure():

    print("Starting data migration for data structure...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find all documents in the collection
    documents = list(collection.find({}))
    print(f"Found {len(documents)} documents to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        updates = {}

        data = doc.get("data")

        # Check if the document needs migration
        if (
            data
            and isinstance(data, dict)
            and "YOUTUBE_VIDEO" not in data
            and "video_id" in data
        ):
            try:
                video_data = data

                def safe_int(value, default=None):
                    if value is None:
                        return default
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return default

                def parse_string_list(value):
                    if isinstance(value, list):
                        return value
                    if isinstance(value, str):
                        try:
                            return ast.literal_eval(value)
                        except (ValueError, SyntaxError):
                            return []
                    return []

                def parse_iso_date(date_str):
                    if not date_str:
                        return None
                    try:
                        # Attempt to parse with microseconds
                        return datetime.fromisoformat(date_str).timestamp()
                    except (ValueError, TypeError):
                        return None

                created_at_ts = parse_iso_date(video_data.get("created_at"))
                if not created_at_ts:
                    raise RuntimeError("created_at not parsed!")

                video_details_payload = {
                    "video_id": video_data.get("video_id"),
                    "title": video_data.get("title"),
                    "channel_id": video_data.get("channel_id"),
                    "channel_name": video_data.get("channel_name"),
                    "views": safe_int(video_data.get("views"), 0),
                    "description": video_data.get("description"),
                    "thumbnail": video_data.get("thumbnail"),
                    "release_date": parse_iso_date(video_data.get("release_date")),
                    "created_at": created_at_ts,
                    "tags": parse_string_list(video_data.get("tags")),
                    "categories": parse_string_list(video_data.get("categories")),
                    "language": video_data.get("language"),
                    "duration_in_seconds": safe_int(
                        video_data.get("duration_in_seconds")
                    ),
                    "comments_count": safe_int(video_data.get("comments_count")),
                    "likes_count": safe_int(video_data.get("likes_count")),
                }

                video_details = YouTubeVideoDetailsDB(**video_details_payload)

                new_data_field = {
                    "YOUTUBE_VIDEO": video_details.dict(
                        by_alias=True, exclude_none=True
                    )
                }

                updates["data"] = new_data_field

            except Exception as e:
                print(f"Error processing document {doc_id}: {e}")
                continue

        if updates:
            collection.update_one({"_id": doc_id}, {"$set": updates})
            updated_count += 1
            print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_status_details_timestamps():
    """
    Migration script to update created_at fields in the status_details array
    from string timestamps to epoch timestamps.
    """
    print("Starting data migration for status_details timestamps...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find all documents in the collection that have status_details
    documents = list(collection.find({"status_details": {"$exists": True}}))
    print(f"Found {len(documents)} documents with status_details to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        status_details = doc.get("status_details", [])

        if not isinstance(status_details, list):
            print(f"Skipping doc {doc_id}: status_details is not a list.")
            continue

        made_change = False
        new_status_details = []
        for detail in status_details:
            if (
                isinstance(detail, dict)
                and "created_at" in detail
                and isinstance(detail["created_at"], str)
            ):
                try:
                    created_at_str = detail["created_at"]

                    if created_at_str.endswith("+00:00Z"):
                        created_at_str = created_at_str[:-1]
                    elif created_at_str.endswith("Z"):
                        created_at_str = created_at_str[:-1] + "+00:00"

                    dt_obj = datetime.fromisoformat(created_at_str)
                    detail["created_at"] = dt_obj.timestamp()
                    made_change = True
                except (ValueError, TypeError) as e:
                    print(
                        f"Could not parse created_at for doc {doc_id} in status_details: {detail['created_at']}. Error: {e}"
                    )
            new_status_details.append(detail)

        if made_change:
            collection.update_one(
                {"_id": doc_id}, {"$set": {"status_details": new_status_details}}
            )
            updated_count += 1
            print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_status_value():
    """
    Migration script to update status values from 'PROCESSED' to 'PROCESSING'.
    """
    print("Starting data migration for status value...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find documents that need migration
    query = {"$or": [{"status": "PROCESSED"}, {"status_details.status": "PROCESSED"}]}
    documents = list(collection.find(query))
    print(f"Found {len(documents)} documents to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        updates = {}

        # Check and update top-level status
        if doc.get("status") == "PROCESSED":
            updates["status"] = "PROCESSING"

        # Check and update status in status_details
        if "status_details" in doc and isinstance(doc["status_details"], list):
            new_status_details = doc["status_details"]
            details_changed = False
            for detail in new_status_details:
                if isinstance(detail, dict) and detail.get("status") == "PROCESSED":
                    detail["status"] = "PROCESSING"
                    details_changed = True
            if details_changed:
                updates["status_details"] = new_status_details

        if updates:
            collection.update_one({"_id": doc_id}, {"$set": updates})
            updated_count += 1
            print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_add_moderation_passed_sub_status():
    """
    Migration script to add sub_status='MODERATION_PASSED' for documents
    with status='PROCESSING'.
    """
    print("Starting data migration for adding moderation passed sub_status...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find documents that need migration
    query = {"status": "PROCESSING"}
    documents = list(collection.find(query))
    print(f"Found {len(documents)} documents to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]

        if doc.get("sub_status") == "MODERATION_PASSED":
            continue

        processing_status_detail = None
        if "status_details" in doc and isinstance(doc["status_details"], list):
            for detail in doc["status_details"]:
                if isinstance(detail, dict) and detail.get("status") == "PROCESSING":
                    processing_status_detail = detail
                    break

        if not processing_status_detail or "created_at" not in processing_status_detail:
            print(
                f"Skipping doc {doc_id}: No 'PROCESSING' status detail with a timestamp found."
            )
            continue

        created_at_ts = processing_status_detail["created_at"]
        updates = {}

        updates["sub_status"] = "MODERATION_PASSED"

        new_sub_status_detail = {
            "sub_status": "MODERATION_PASSED",
            "created_at": created_at_ts,
            "reason": "First round of moderation passed",
        }

        current_sub_status_details = doc.get("sub_status_details", [])
        current_sub_status_details.append(new_sub_status_detail)
        updates["sub_status_details"] = current_sub_status_details

        if updates:
            collection.update_one({"_id": doc_id}, {"$set": updates})
            updated_count += 1
            print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_enrich_subtitles():
    """
    Migration script to enrich documents with subtitles if they are missing.
    """
    print("Starting data migration for enriching subtitles...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    youtube_tool = YouTubeExternalTool()

    # Find documents that need migration
    query = {
        "data.YOUTUBE_VIDEO": {"$exists": True},
        "data.YOUTUBE_VIDEO.subtitles": {"$exists": False},
    }
    documents = list(collection.find(query))
    print(f"Found {len(documents)} documents to process for subtitle enrichment.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        try:
            video_data_db_dict = doc["data"]["YOUTUBE_VIDEO"]

            video_details_db = YouTubeVideoDetailsDB(**video_data_db_dict)
            video_details_entity = YouTubeVideoDetailsAdapter.from_db_model(
                video_details_db
            )

            enriched_videos = youtube_tool.enrich_video_data_with_details(
                youtube_video_details=[video_details_entity]
            )

            if enriched_videos and enriched_videos[0].subtitles:
                enriched_video_db = YouTubeVideoDetailsAdapter.to_db_model(
                    enriched_videos[0]
                )
                updates = {"data.YOUTUBE_VIDEO": enriched_video_db.dict(by_alias=True)}
                collection.update_one({"_id": doc_id}, {"$set": updates})
                updated_count += 1
                print(f"Updated document {doc_id} with subtitles.")
            else:
                print(f"Could not enrich document {doc_id} with subtitles.")

        except Exception as e:
            print(f"Error processing document {doc_id}: {e}")
            continue

    print(f"Subtitle enrichment migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_delete_subtitles():
    """
    Migration script to delete the subtitles object from all documents.
    """
    print("Starting data migration for deleting subtitles...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find documents that have subtitles and remove the subtitles field
    query = {"data.YOUTUBE_VIDEO.subtitles": {"$exists": True}}
    update_operation = {"$unset": {"data.YOUTUBE_VIDEO.subtitles": ""}}

    result = collection.update_many(query, update_operation)

    print(
        f"Subtitle deletion migration complete. {result.modified_count} documents updated."
    )

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


def migrate_add_missing_sub_status():
    """
    Migration script to add sub_status='MODERATION_PASSED' for documents
    with status='PROCESSING' but missing sub_status field.
    """
    print("Starting data migration for adding missing sub_status...")

    # Connect to MongoDB
    MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    collection = db[settings.COLLECTION_NAME]

    print(
        f"Connected to database '{settings.DATABASE_NAME}' and collection '{settings.COLLECTION_NAME}'."
    )

    # Find documents that need migration
    query = {"sub_status": {"$exists": False}, "status": "PROCESSING"}
    documents = list(collection.find(query))
    print(f"Found {len(documents)} documents to process.")

    updated_count = 0
    for doc in documents:
        doc_id = doc["_id"]
        updates = {}

        # Get the timestamp from the most recent PROCESSING status detail
        processing_timestamp = None
        if "status_details" in doc and isinstance(doc["status_details"], list):
            for detail in doc["status_details"]:
                if isinstance(detail, dict) and detail.get("status") == "PROCESSING":
                    if "created_at" in detail:
                        processing_timestamp = detail["created_at"]
                        break

        # If no PROCESSING timestamp found, use current time
        if not processing_timestamp:
            processing_timestamp = datetime.now().timestamp()

        updates["sub_status"] = "MODERATION_PASSED"

        new_sub_status_detail = {
            "sub_status": "MODERATION_PASSED",
            "created_at": processing_timestamp,
            "reason": "first moderation passed",
        }

        current_sub_status_details = doc.get("sub_status_details", [])
        current_sub_status_details.append(new_sub_status_detail)
        updates["sub_status_details"] = current_sub_status_details

        if updates:
            collection.update_one({"_id": doc_id}, {"$set": updates})
            updated_count += 1
            print(f"Updated document {doc_id}")

    print(f"Migration complete. {updated_count} documents updated.")

    # Close the connection
    MongoDB.close_database_connection()
    print("Database connection closed.")


if __name__ == "__main__":
    # migrate_timestamps()
    # migrate_status_details_timestamps()
    # migrate_status_value()
    # migrate_add_moderation_passed_sub_status()
    # migrate_enrich_subtitles()
    # migrate_delete_subtitles()
    migrate_add_missing_sub_status()
