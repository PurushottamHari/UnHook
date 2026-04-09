import asyncio
import os
import sys

from repositories.mongodb.config.database import MongoDB
from repositories.mongodb.config.settings import get_mongodb_settings


async def migrate_user_schedule():
    """
    Migration script to move weekdays from interested list to the new schedule field.
    """
    print("Starting data migration for user schedule...")

    # Connect to MongoDB
    await MongoDB.connect_to_database()
    db = MongoDB.get_database()
    settings = get_mongodb_settings()
    users_collection = db[settings.COLLECTION_NAME]

    print(f"Connected to {settings.COLLECTION_NAME} collection.")

    # Find all users
    cursor = users_collection.find({})
    users = await cursor.to_list(length=None)
    print(f"Found {len(users)} users to process.")

    updated_count = 0
    for user_doc in users:
        user_id = user_doc["_id"]
        interested = user_doc.get("interested", [])

        # 1. Group categories by weekday
        weekday_map = {}  # Weekday str -> Set of CategoryName str

        new_interested = []
        for interest in interested:
            category_name = interest.get("category_name")
            weekdays = interest.get("weekdays", [])

            for day in weekdays:
                if day not in weekday_map:
                    weekday_map[day] = set()
                weekday_map[day].add(category_name)

            # Remove weekdays from interest
            interest_copy = interest.copy()
            if "weekdays" in interest_copy:
                del interest_copy["weekdays"]
            new_interested.append(interest_copy)

        # 2. Create schedule rules
        rules = []
        for day, categories in weekday_map.items():
            rules.append(
                {
                    "rule_type": "WEEKDAY",
                    "rule_value": day,
                    "content": {
                        "allowed_categories": list(categories),
                        "youtube_channels": [],
                    },
                }
            )

        new_schedule = {"rules": rules}

        # --- Dry Run: Print Before and After ---
        print(f"\n--- User: {user_id} ---")
        print("BEFORE (Interested):")
        for i in interested:
            print(f"  - {i}")

        print("AFTER (Interested - without weekdays):")
        for i in new_interested:
            print(f"  - {i}")

        print("AFTER (New Schedule):")
        import json

        # Helper to handle sets in json serialization for printing
        def set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        print(json.dumps(new_schedule, indent=2, default=set_default))
        print("--------------------------\n")

        # 3. Update document (COMMENTED OUT FOR DRY RUN)
        update_result = await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"interested": new_interested, "schedule": new_schedule}},
        )

        if update_result.modified_count > 0:
            updated_count += 1
            print(f"Updated user {user_id}")
        else:
            print(f"No changes for user {user_id}")

    print(f"Migration complete. {updated_count} users updated.")

    # Close the connection
    await MongoDB.close_database_connection()
    print("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(migrate_user_schedule())
