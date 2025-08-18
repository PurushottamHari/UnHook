#!/usr/bin/env python3
"""
Test script to demonstrate the allowed categories API endpoints.
"""

import json
from datetime import datetime, timedelta

import requests

# Base URL for the Flask app
BASE_URL = "http://localhost:5000"


def test_all_categories():
    """Test the /api/categories endpoint."""
    print("=== Testing All Categories Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/categories")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {data['total_categories']} available categories:")
        for category in data["available_categories"]:
            print(f"  - {category}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

    print()


def test_allowed_categories_for_user(user_id, date=None):
    """Test the /api/user/{user_id}/allowed-categories endpoint."""
    print(f"=== Testing Categories for User {user_id} ===")

    url = f"{BASE_URL}/api/user/{user_id}/allowed-categories"
    if date:
        url += f"?date={date}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! For {data['date']} ({data['weekday']}):")
        print(f"  User ID: {data['user_id']}")
        print(f"  Total allowed categories: {data['total_allowed_categories']}")
        print(f"  Total newspaper categories: {data['total_newspaper_categories']}")
        print(f"  Total articles: {data['total_articles']}")

        if data["newspaper_categories"]:
            print("  📰 Newspaper categories:")
            for category in data["newspaper_categories"]:
                print(
                    f"    - {category['category_name']} ({category['article_count']} articles)"
                )
                for article in category["articles"][:2]:  # Show first 2 articles
                    print(f"      • {article['title'][:50]}...")
                if category["article_count"] > 2:
                    print(
                        f"      • ... and {category['article_count'] - 2} more articles"
                    )
                print()
        else:
            print("  📰 No categories found in newspaper for this day.")

        if data["allowed_categories"]:
            print("  ⚙️  Allowed categories (user preferences):")
            for category in data["allowed_categories"]:
                print(f"    - {category['category_name']}")
                print(f"      Definition: {category['category_definition']}")
                print(f"      Output Type: {category['output_type']}")
                print(f"      Weekdays: {', '.join(category['weekdays'])}")
                print()
        else:
            print("  ⚙️  No categories allowed by user preferences for this day.")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

    print()


def test_multiple_dates(user_id):
    """Test allowed categories for multiple dates."""
    print(f"=== Testing Allowed Categories for Multiple Dates (User {user_id}) ===")

    # Test for the next 7 days
    for i in range(7):
        test_date = datetime.now() + timedelta(days=i)
        date_str = test_date.strftime("%Y-%m-%d")
        test_allowed_categories_for_user(user_id, date_str)


if __name__ == "__main__":
    # Default user ID from the app
    default_user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"

    print("🚀 Testing Allowed Categories API Endpoints")
    print("=" * 50)

    # Test all available categories
    test_all_categories()

    # Test allowed categories for today
    test_allowed_categories_for_user(default_user_id)

    # Test allowed categories for a specific date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    test_allowed_categories_for_user(default_user_id, tomorrow)

    # Test for multiple dates
    test_multiple_dates(default_user_id)

    print("✅ Testing complete!")
