import os
import sys
from calendar import weekday

from pymongo import UpdateOne

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from datetime import datetime

import pytz

from data_collector_service.models.user_collected_content import ContentStatus
from newspaper_service.repositories.mongodb.config.database import MongoDB
from newspaper_service.repositories.mongodb.config.settings import \
    get_mongodb_settings
from newspaper_service.repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from user_service.models.enums import Weekday


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


def migrate_candidate_links_to_include_source_list():
    """
    Migration script to populate links.source_list in NewspaperArticleCandidate.
    Uses links.user_collected_content_id to fetch external_id and content_type
    from the collected_content collection.
    """
    try:
        from data_collector_service.models.enums import ContentType
        from newspaper_service.models import SourceType

        # Get database connection
        db = MongoDB.get_database()
        settings = get_mongodb_settings()

        candidates_collection = db[settings.NEWSPAPER_ARTICLE_CANDIDATE_COLLECTION_NAME]
        content_collection = db[settings.USER_COLLECTED_CONTENT_COLLECTION_NAME]

        generated_content_collection = db["generated_content"]

        # Find candidates where source_list is missing or empty
        # We also want to make sure user_collected_content_id is present
        query = {
            "$or": [
                {"links.source_list": {"$exists": False}},
                {"links.source_list": {"$size": 0}},
                {"links.source_list": None},
            ],
            "links.user_collected_content_id": {"$exists": True, "$ne": None},
        }

        candidates = list(candidates_collection.find(query))
        print(f"Found {len(candidates)} candidates to migrate")

        updated_count = 0
        operations = []

        for candidate_doc in candidates:
            candidate_id = candidate_doc["_id"]
            user_collected_content_id = candidate_doc["links"][
                "user_collected_content_id"
            ]

            # Fetch the content document
            content_doc = content_collection.find_one(
                {"_id": user_collected_content_id}
            )

            if not content_doc:
                print(
                    f"Content document {user_collected_content_id} not found for candidate {candidate_id}"
                )
                continue

            external_id = content_doc.get("external_id")
            content_type_str = content_doc.get("content_type")

            if not external_id:
                print(f"External ID not found for content {user_collected_content_id}")
                continue

            # Fetch generated content to get generated_content_id
            generated_content_doc = generated_content_collection.find_one(
                {"external_id": external_id}
            )
            generated_content_id = (
                generated_content_doc["_id"] if generated_content_doc else None
            )

            # Map content_type to source_type
            source_type = SourceType.YOUTUBE_VIDEO.value  # Default
            if content_type_str == ContentType.YOUTUBE_VIDEO.value:
                source_type = SourceType.YOUTUBE_VIDEO.value

            # Create source_list entry
            source_detail = {
                "external_id": external_id,
                "source_type": source_type,
                "metadata": {},
            }

            # Prepare update document
            update_fields = {
                "links.source_list": [source_detail],
                "updated_at": datetime.utcnow().replace(tzinfo=pytz.UTC).timestamp(),
            }

            update_fields["links.generated_content_id"] = generated_content_id
            update_fields["links.generated_content_id_list"] = (
                [generated_content_id] if generated_content_id else []
            )

            # Collect update operation
            operations.append(
                UpdateOne(
                    {"_id": candidate_id},
                    {
                        "$set": update_fields,
                        "$inc": {"version": 1},
                    },
                )
            )

        # Execute bulk update
        if operations:
            print(f"Executing bulk update for {len(operations)} candidates...")
            result = candidates_collection.bulk_write(operations)
            updated_count = result.modified_count
            print(f"Successfully migrated {updated_count} candidates")
        else:
            print("No candidates found to migrate.")

        pass

    except Exception as e:
        print(f"Error in migrate_candidate_links_to_include_source_list: {str(e)}")
        raise


def migrate_newspapers_v1_to_v2():
    """
    Migration script to migrate newspapers from V1 to V2 and create
    corresponding NewspaperArticleCandidate documents.
    """
    import uuid

    from data_collector_service.models.enums import ContentType
    from newspaper_service.models import (CandidateSource, CandidateStatus,
                                          CandidateType, NewspaperV2,
                                          SourceType)

    try:
        # Get database connection
        db = MongoDB.get_database()
        settings = get_mongodb_settings()

        v1_collection = db[settings.NEWSPAPER_COLLECTION_NAME]
        v2_collection = db[settings.NEWSPAPER_V2_COLLECTION_NAME]
        candidates_collection = db[settings.NEWSPAPER_ARTICLE_CANDIDATE_COLLECTION_NAME]
        content_collection = db[settings.USER_COLLECTED_CONTENT_COLLECTION_NAME]
        youtube_collection = db[settings.YOUTUBE_COLLECTED_CONTENT_COLLECTION_NAME]
        generated_content_collection = db["generated_content"]

        # Fetch all V1 newspapers
        print("Fetching V1 newspapers...")
        v1_newspapers = list(v1_collection.find())
        print(f"Found {len(v1_newspapers)} V1 newspapers to migrate")

        v2_operations = []
        candidate_operations = []

        batch_size = 15
        for i, v1_doc in enumerate(v1_newspapers):
            newspaper_id = v1_doc["_id"]
            user_id = v1_doc["user_id"]
            print(
                f"[{i+1}/{len(v1_newspapers)}] Processing newspaper {newspaper_id} for user {user_id}..."
            )

            # 1. Create NewspaperV2 document
            # Preserve metadata exactly
            v2_doc = {
                "_id": newspaper_id,
                "user_id": user_id,
                "status": v1_doc["status"],
                "status_details": v1_doc.get("status_details", []),
                "reading_time_in_seconds": v1_doc.get("reading_time_in_seconds", 0),
                "version": 1,
                "created_at": v1_doc["created_at"],
                "updated_at": v1_doc["updated_at"],
            }

            v2_operations.append(
                UpdateOne({"_id": newspaper_id}, {"$set": v2_doc}, upsert=True)
            )

            # 2. Process considered_content_list to create candidates
            considered_items = v1_doc.get("considered_content_list", [])
            print(
                f"Processing {len(considered_items)} considered_content_list items for newspaper {newspaper_id}..."
            )
            for item in considered_items:
                content_id = item["user_collected_content_id"]
                v1_status = item.get("considered_content_status")

                # Only process if status is ACCEPTED (to be marked as USED)
                # or as requested by the user to mark them as USED.
                if v1_status != "ACCEPTED":
                    continue

                # Fetch collected content
                content_doc = content_collection.find_one({"_id": content_id})
                if not content_doc:
                    raise ValueError(
                        f"Collected content {content_id} not found for newspaper {newspaper_id}"
                    )

                external_id = content_doc["external_id"]
                content_type_str = content_doc["content_type"]

                # Fetch generated content
                gen_content_doc = generated_content_collection.find_one(
                    {"external_id": external_id}
                )
                if not gen_content_doc:
                    raise ValueError(
                        f"Generated content not found for external_id {external_id}"
                    )

                # Fetch source details
                metadata = {}
                source_type = SourceType.YOUTUBE_VIDEO.value  # Default
                if content_type_str == ContentType.YOUTUBE_VIDEO.value:
                    source_type = SourceType.YOUTUBE_VIDEO.value
                    youtube_doc = youtube_collection.find_one({"video_id": external_id})
                    if not youtube_doc:
                        raise ValueError(
                            f"YouTube details not found for video_id {external_id}"
                        )

                    metadata = {
                        "youtube_video_link": f"https://www.youtube.com/watch?v={external_id}",
                        "channel_name": youtube_doc.get("channel_name", ""),
                    }
                else:
                    # If not YouTube, we still check for other sources if they exist, but here we expect clean migration
                    raise ValueError(
                        f"Unsupported content type {content_type_str} for clean migration"
                    )

                # Construct Candidate
                candidate_id = str(uuid.uuid4())

                # Status details
                # 1. CONSIDERED at newspaper created_at
                # 2. USED at newspaper updated_at
                status_details = [
                    {
                        "status": CandidateStatus.CONSIDERED.value,
                        "created_at": v1_doc["created_at"],
                        "reason": "Migration: Initial state from V1 newspaper",
                    },
                    {
                        "status": CandidateStatus.USED.value,
                        "created_at": v1_doc["updated_at"],
                        "reason": "Migration: Marked as USED based on V1 final_content_list",
                    },
                ]

                candidate_doc = {
                    "_id": candidate_id,
                    "linked_id": content_id,
                    "source": CandidateSource.USER_COLLECTED_CONTENT.value,
                    "type": CandidateType.USER_COLLECTED_CONTENT.value,
                    "user_id": user_id,
                    "links": {
                        "user_collected_content_id": content_id,
                        "generated_content_id": gen_content_doc["_id"],
                        "generated_content_id_list": [gen_content_doc["_id"]],
                        "source_list": [
                            {
                                "external_id": external_id,
                                "source_type": source_type,
                                "metadata": metadata,
                            }
                        ],
                    },
                    "newspaper_id": newspaper_id,
                    "status": CandidateStatus.USED.value,
                    "status_details": status_details,
                    "version": 1,
                    "created_at": v1_doc["created_at"],
                    "updated_at": v1_doc["updated_at"],
                }

                candidate_operations.append(
                    UpdateOne(
                        {"linked_id": content_id}, {"$set": candidate_doc}, upsert=True
                    )
                )

            # Execute batch writes every batch_size newspapers
            if (i + 1) % batch_size == 0 or (i + 1) == len(v1_newspapers):
                if v2_operations:
                    print(f"Upserting batch of {len(v2_operations)} V2 newspapers...")
                    v2_collection.bulk_write(v2_operations)
                    v2_operations = []

                if candidate_operations:
                    print(
                        f"Upserting batch of {len(candidate_operations)} candidates..."
                    )
                    candidates_collection.bulk_write(candidate_operations)
                    candidate_operations = []

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise


if __name__ == "__main__":

    # Example usage for the migration functions

    # To run the V1 to V2 migration:
    print("Starting V1 to V2 migration...")
    migrate_newspapers_v1_to_v2()

    # To fix newspaper created_at dates based on content dates:
    # fix_newspaper_created_at_dates()
