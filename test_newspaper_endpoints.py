"""
Temporary test script for newspaper service endpoints.
Tests all endpoints in newspaper_controller.py and generated_content_controller.py
"""

import json
import shlex
from urllib.parse import quote, urlencode

import requests

# Configuration
BASE_URL = "https://unhook-production-b172.up.railway.app"
TEST_USER_ID = "607d95f0-47ef-444c-89d2-d05f257d1265"
TEST_NEWSPAPER_ID = (
    "fe207d6e-8151-4bd8-9b06-3f91bc259740"  # Replace with actual ID from your DB
)
TEST_CONTENT_EXTERNAL_ID = (
    "0Aaq1b5_uBQ"  # External ID of the generated content (e.g., YouTube video ID)
)
# For interaction endpoints, we need the MongoDB internal _id, not external_id
# You can get this by calling GET /generated_content/{external_id} first and using the 'id' field from the response
TEST_GENERATED_CONTENT_ID = "4b446a44-f9db-4b28-9bc8-e6bf38638d46"  # MongoDB _id (internal ID) - get from GET /generated_content/{external_id}


def print_curl_command(method, url, headers=None, params=None, json_data=None):
    """Helper function to print curl command equivalent."""
    curl_parts = ["curl", "-X", method]

    # Add headers
    if headers:
        for key, value in headers.items():
            curl_parts.extend(["-H", shlex.quote(f"{key}: {value}")])

    # Add Content-Type for POST requests with JSON
    if method.upper() == "POST" and json_data:
        curl_parts.extend(["-H", shlex.quote("Content-Type: application/json")])

    # Add query parameters
    if params:
        # Filter out None values
        filtered_params = {k: v for k, v in params.items() if v is not None}
        if filtered_params:
            query_string = urlencode(filtered_params)
            url = f"{url}?{query_string}"

    # Add URL (properly quoted for shell)
    curl_parts.append(shlex.quote(url))

    # Add JSON body
    if json_data:
        json_str = json.dumps(json_data)
        curl_parts.extend(["-d", shlex.quote(json_str)])

    curl_command = " ".join(curl_parts)
    print(f"\nCURL Command:")
    print(f"{curl_command}\n")


def print_response(title, response):
    """Helper function to print formatted response."""
    print(f"Status Code: {response.status_code}")
    if response.status_code >= 400:
        try:
            error_detail = response.json().get("detail", response.text)
            print(f"Error: {error_detail}")
        except:
            print(f"Error: {response.text[:200]}")  # First 200 chars of error


# ============================================================================
# NEWSPAPER CONTROLLER ENDPOINTS
# ============================================================================

print("\n" + "=" * 60)
print("TESTING NEWSPAPER CONTROLLER ENDPOINTS")
print("=" * 60)

# 1. GET /newspapers/{newspaper_id}
print("\n1. Testing GET /newspapers/{newspaper_id}")
print_curl_command(
    "GET",
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}",
    headers={"X-User-ID": TEST_USER_ID},
)
response = requests.get(
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}", headers={"X-User-ID": TEST_USER_ID}
)
print_response("GET /newspapers/{newspaper_id}", response)

# 2. GET /newspapers (without filters)
print("\n2. Testing GET /newspapers (no filters)")
print_curl_command("GET", f"{BASE_URL}/newspapers", headers={"X-User-ID": TEST_USER_ID})
response = requests.get(f"{BASE_URL}/newspapers", headers={"X-User-ID": TEST_USER_ID})
print_response("GET /newspapers (no filters)", response)

# 3. GET /newspapers (with date filter)
print("\n3. Testing GET /newspapers (with date filter)")
print_curl_command(
    "GET",
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID},
    params={"date": "25/01/2025"},
)
response = requests.get(
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID},
    params={"date": "25/01/2025"},
)
print_response("GET /newspapers (with date filter)", response)

# 4. GET /newspapers (with pagination)
print("\n4. Testing GET /newspapers (with pagination)")
print_curl_command(
    "GET",
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5},
)
response = requests.get(
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5, "starting_after": None},
)
print_response("GET /newspapers (with pagination)", response)


# ============================================================================
# GENERATED CONTENT CONTROLLER ENDPOINTS
# ============================================================================

print("\n" + "=" * 60)
print("TESTING GENERATED CONTENT CONTROLLER ENDPOINTS")
print("=" * 60)

# 5. POST /generated_content/{generated_content_id}/user_interaction
print("\n5. Testing POST /generated_content/{generated_content_id}/user_interaction")
json_body = {
    "user_id": TEST_USER_ID,
    "interaction_type": "LIKE",
    "metadata": {"source": "test"},
}
print_curl_command(
    "POST",
    f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction",
    json_data=json_body,
)
response = requests.post(
    f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction",
    json=json_body,
)
print_response("POST /generated_content/{id}/user_interaction (LIKE)", response)

# Try different interaction types
for interaction_type in ["DISLIKE", "SAVED", "REPORT"]:
    print(f"\n5.{interaction_type}. Testing POST with {interaction_type}")
    json_body = {
        "user_id": TEST_USER_ID,
        "interaction_type": interaction_type,
        "metadata": {"source": "test"},
    }
    print_curl_command(
        "POST",
        f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction",
        json_data=json_body,
    )
    response = requests.post(
        f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction",
        json=json_body,
    )
    print_response(
        f"POST /generated_content/{{id}}/user_interaction ({interaction_type})",
        response,
    )

# 6. GET /list_user_interactions_for_content/{content_id}
print("\n6. Testing GET /list_user_interactions_for_content/{content_id}")
print_curl_command(
    "GET", f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}"
)
response = requests.get(
    f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}"
)
print_response("GET /list_user_interactions_for_content/{content_id}", response)

# 7. GET /list_user_interactions_for_content/{content_id} (with pagination)
print(
    "\n7. Testing GET /list_user_interactions_for_content/{content_id} (with pagination)"
)
print_curl_command(
    "GET",
    f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}",
    params={"page_limit": 5},
)
response = requests.get(
    f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}",
    params={"page_limit": 5, "starting_after": None},
)
print_response(
    "GET /list_user_interactions_for_content/{content_id} (pagination)", response
)

# 8. GET /list_user_interactions (no filters)
print("\n8. Testing GET /list_user_interactions (no filters)")
print_curl_command(
    "GET", f"{BASE_URL}/list_user_interactions", headers={"X-User-ID": TEST_USER_ID}
)
response = requests.get(
    f"{BASE_URL}/list_user_interactions", headers={"X-User-ID": TEST_USER_ID}
)
print_response("GET /list_user_interactions (no filters)", response)

# 9. GET /list_user_interactions (with interaction_type filter)
print("\n9. Testing GET /list_user_interactions (with interaction_type filter)")
for interaction_type in ["LIKE", "DISLIKE", "SAVED", "REPORT"]:
    print(f"\n9.{interaction_type}. Testing with filter: {interaction_type}")
    print_curl_command(
        "GET",
        f"{BASE_URL}/list_user_interactions",
        headers={"X-User-ID": TEST_USER_ID},
        params={"interaction_type": interaction_type},
    )
    response = requests.get(
        f"{BASE_URL}/list_user_interactions",
        headers={"X-User-ID": TEST_USER_ID},
        params={"interaction_type": interaction_type},
    )
    print_response(
        f"GET /list_user_interactions (filter: {interaction_type})", response
    )

# 10. GET /list_user_interactions (with pagination)
print("\n10. Testing GET /list_user_interactions (with pagination)")
print_curl_command(
    "GET",
    f"{BASE_URL}/list_user_interactions",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5},
)
response = requests.get(
    f"{BASE_URL}/list_user_interactions",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5, "starting_after": None},
)
print_response("GET /list_user_interactions (with pagination)", response)

# 11. GET /generated_content/{content_id} (uses MongoDB _id)
print("\n11. Testing GET /generated_content/{content_id} (uses MongoDB _id)")
print_curl_command("GET", f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}")
response = requests.get(f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}")
print_response("GET /generated_content/{content_id}", response)

# 12. GET /newspapers/{newspaper_id}/generated_content (now includes active interactions)
print(
    "\n12. Testing GET /newspapers/{newspaper_id}/generated_content (includes active interactions)"
)
print_curl_command(
    "GET",
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content",
    headers={"X-User-ID": TEST_USER_ID},
)
response = requests.get(
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content",
    headers={"X-User-ID": TEST_USER_ID},
)
print_response("GET /newspapers/{newspaper_id}/generated_content", response)
# Print response structure to verify interactions are included
if response.status_code == 200:
    try:
        data = response.json()
        if "data" in data and "list_response" in data["data"]:
            if len(data["data"]["list_response"]) > 0:
                first_item = data["data"]["list_response"][0]
                print(f"\nResponse structure check:")
                print(
                    f"  - Has 'generated_content': {'generated_content' in first_item}"
                )
                print(
                    f"  - Has 'active_user_interactions': {'active_user_interactions' in first_item}"
                )
                if "active_user_interactions" in first_item:
                    interactions = first_item["active_user_interactions"]
                    print(f"  - Number of active interactions: {len(interactions)}")
                    if interactions:
                        print(
                            f"  - Interaction types: {[i.get('interaction_type') for i in interactions]}"
                        )
    except Exception as e:
        print(f"  Could not parse response structure: {e}")

# 13. GET /newspapers/{newspaper_id}/generated_content (with pagination)
print(
    "\n13. Testing GET /newspapers/{newspaper_id}/generated_content (with pagination)"
)
print_curl_command(
    "GET",
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5},
)
response = requests.get(
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5, "starting_after": None},
)
print_response(
    "GET /newspapers/{newspaper_id}/generated_content (pagination)", response
)


# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
print(
    "\nNote: Update TEST_NEWSPAPER_ID, TEST_CONTENT_EXTERNAL_ID, and TEST_GENERATED_CONTENT_ID"
)
print(
    "at the top of this script with actual IDs from your database for accurate testing."
)
print("\nImportant:")
print(
    "- TEST_CONTENT_EXTERNAL_ID: External ID (e.g., YouTube video ID) - used for reference only"
)
print(
    "- TEST_GENERATED_CONTENT_ID: MongoDB internal _id - used for GET /generated_content/{content_id} and interaction endpoints"
)
print("- GET /generated_content/{content_id} now uses MongoDB _id, not external_id")
print("- Interaction endpoints use MongoDB internal _id")
print(
    "- GET /newspapers/{newspaper_id}/generated_content now requires X-User-ID header and includes active_user_interactions"
)
