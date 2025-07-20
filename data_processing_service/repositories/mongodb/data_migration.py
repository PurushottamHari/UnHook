import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel


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


if __name__ == "__main__":
    migrate_generated_content_status_details()
