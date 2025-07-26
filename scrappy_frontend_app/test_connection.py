#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and data access.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config import CONFIG
from pymongo import MongoClient


def test_mongodb_connection():
    """Test MongoDB connection and data access."""
    print("🔍 Testing MongoDB connection...")
    print(f"📊 MongoDB URI: {CONFIG['MONGODB_URI']}")
    print(f"🗄️  Database: {CONFIG['DATABASE_NAME']}")
    print("-" * 50)

    try:
        # Test connection
        client = MongoClient(CONFIG["MONGODB_URI"])
        db = client[CONFIG["DATABASE_NAME"]]

        # Test database access
        collections = db.list_collection_names()
        print(f"✅ Connected to MongoDB successfully!")
        print(f"📁 Available collections: {collections}")

        # Test generated_content collection
        if "generated_content" in collections:
            collection = db.generated_content

            # Count total documents
            total_count = collection.count_documents({})
            print(f"📄 Total documents in generated_content: {total_count}")

            # Count articles with ARTICLE_GENERATED status
            from data_processing_service.models.generated_content import \
                GeneratedContentStatus

            article_count = collection.count_documents(
                {"status": GeneratedContentStatus.ARTICLE_GENERATED}
            )
            print(f"📰 Articles with ARTICLE_GENERATED status: {article_count}")

            # Show sample article
            if article_count > 0:
                sample = collection.find_one(
                    {"status": GeneratedContentStatus.ARTICLE_GENERATED}
                )
                print(f"\n📋 Sample article:")
                print(f"   ID: {sample.get('_id')}")
                print(f"   Status: {sample.get('status')}")
                print(f"   Content Type: {sample.get('content_type')}")

                generated = sample.get("generated", {})
                if "VERY_SHORT" in generated:
                    print(
                        f"   Title: {generated['VERY_SHORT'].get('string', 'N/A')[:50]}..."
                    )
                if "SHORT" in generated:
                    print(
                        f"   Summary: {generated['SHORT'].get('string', 'N/A')[:100]}..."
                    )

                if "LONG" in generated or "MEDIUM" in generated:
                    content_type = "LONG" if "LONG" in generated else "MEDIUM"
                    content = generated[content_type].get(
                        "markdown_string", generated[content_type].get("string", "")
                    )
                    print(f"   Content ({content_type}): {content[:100]}...")
            else:
                print("⚠️  No articles with ARTICLE_GENERATED status found!")
                print(
                    "   Make sure your content processing pipeline has generated some articles."
                )

        else:
            print("❌ generated_content collection not found!")
            print("   Make sure you're connected to the correct database.")

        client.close()
        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure MongoDB is running")
        print("   2. Check your MONGODB_URI in the config")
        print("   3. Verify the database name is correct")
        print("   4. Ensure network connectivity to MongoDB")
        return False

    return True


if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
