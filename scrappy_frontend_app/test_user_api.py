#!/usr/bin/env python3
"""
Simple test script to verify user API endpoints work correctly.
"""

import json

import requests

BASE_URL = "http://localhost:5000"


def test_user_api():
    """Test the user API endpoints."""
    user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"

    print("Testing User API endpoints...")
    print("=" * 50)

    # Test GET user
    print("1. Testing GET /api/user/{user_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/user/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Successfully retrieved user data")
            print(f"   User ID: {user_data.get('_id')}")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Email: {user_data.get('email')}")
            print(
                f"   Max Reading Time: {user_data.get('max_reading_time_per_day_mins')} minutes"
            )
        else:
            print(f"❌ Failed to get user: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error getting user: {e}")

    print("\n" + "=" * 50)

    # Test PUT user (update)
    print("2. Testing PUT /api/user/{user_id}")
    try:
        # Get current user data first
        response = requests.get(f"{BASE_URL}/api/user/{user_id}")
        if response.status_code == 200:
            user_data = response.json()

            # Update max reading time
            update_data = {
                "max_reading_time_per_day_mins": user_data.get(
                    "max_reading_time_per_day_mins", 30
                )
                + 5
            }

            response = requests.put(
                f"{BASE_URL}/api/user/{user_id}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(update_data),
            )

            if response.status_code == 200:
                updated_user = response.json()
                print(f"✅ Successfully updated user")
                print(
                    f"   New max reading time: {updated_user.get('max_reading_time_per_day_mins')} minutes"
                )
            else:
                print(
                    f"❌ Failed to update user: {response.status_code} - {response.text}"
                )
        else:
            print(f"❌ Could not get user data for update test")
    except Exception as e:
        print(f"❌ Error updating user: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_user_api()
