#!/usr/bin/env python3
"""
Test script to verify the newspaper functionality.
"""

import sys
from pathlib import Path

# Add the parent directory to Python path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from datetime import datetime

from config import CONFIG
from pymongo import MongoClient


def test_newspaper_functionality():
    """Test the newspaper functionality."""
    print("🔍 Testing newspaper functionality...")
    print(f"📊 MongoDB URI: {CONFIG['MONGODB_URI']}")
    print(f"🗄️  Database: {CONFIG['DATABASE_NAME']}")
    print("-" * 50)

    try:
        # Test connection
        client = MongoClient(CONFIG["MONGODB_URI"])
        db = client[CONFIG["DATABASE_NAME"]]

        # Test user ID
        user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"
        print(f"👤 Testing with user ID: {user_id}")

        # Test newspapers collection
        newspapers = db.newspapers.find({"user_id": user_id})
        count = 0
        for paper in newspapers:
            count += 1
            print(
                f'📰 Newspaper {count}: ID={paper["_id"]}, Status={paper["status"]}, Articles={len(paper.get("considered_content_list", []))}'
            )
        print(f"📊 Total newspapers for user: {count}")

        if count > 0:
            # Test fetching articles for the first newspaper
            first_paper = db.newspapers.find_one({"user_id": user_id})
            if first_paper:
                print(
                    f"\n🔍 Testing article fetching for newspaper: {first_paper['_id']}"
                )

                # Get considered content IDs
                considered_content_ids = []
                for item in first_paper.get("considered_content_list", []):
                    if "user_collected_content_id" in item:
                        considered_content_ids.append(item["user_collected_content_id"])

                print(f"📝 Considered content IDs: {len(considered_content_ids)}")

                if considered_content_ids:
                    # Test fetching generated articles
                    from data_processing_service.models.generated_content import \
                        GeneratedContentStatus
                    from user_service.models.enums import OutputType

                    articles = db.generated_content.find(
                        {
                            "status": GeneratedContentStatus.ARTICLE_GENERATED,
                            "user_collected_content_id": {
                                "$in": considered_content_ids
                            },
                        }
                    )

                    article_count = 0
                    for article in articles:
                        article_count += 1
                        generated = article.get("generated", {})
                        title = ""
                        if OutputType.VERY_SHORT in generated:
                            title = generated[OutputType.VERY_SHORT].get("string", "")
                        elif OutputType.SHORT in generated:
                            summary = generated[OutputType.SHORT].get("string", "")
                            title = (
                                summary.split(".")[0][:50] + "..."
                                if len(summary.split(".")[0]) > 50
                                else summary.split(".")[0]
                            )

                        print(f"   📄 Article {article_count}: {title[:60]}...")

                    print(f"📰 Total articles found: {article_count}")
                else:
                    print("⚠️  No considered content found in this newspaper")
            else:
                print("❌ No newspapers found for user")
        else:
            print("❌ No newspapers found for user")

        client.close()
        print("\n✅ Newspaper functionality test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_newspaper_functionality()
    sys.exit(0 if success else 1)
