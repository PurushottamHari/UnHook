"""
Temporary test script for newspaper service endpoints.
Tests all endpoints in newspaper_controller.py and generated_content_controller.py
"""

import json
import shlex
import requests
from urllib.parse import urlencode, quote

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "607d95f0-47ef-444c-89d2-d05f257d1265"
TEST_NEWSPAPER_ID = "fe207d6e-8151-4bd8-9b06-3f91bc259740"  # Replace with actual ID from your DB
TEST_CONTENT_EXTERNAL_ID = "0Aaq1b5_uBQ"  # External ID of the generated content (e.g., YouTube video ID)
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

print("\n" + "="*60)
print("TESTING NEWSPAPER CONTROLLER ENDPOINTS")
print("="*60)

# 1. GET /newspapers/{newspaper_id}
print("\n1. Testing GET /newspapers/{newspaper_id}")
print_curl_command("GET", f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}", headers={"X-User-ID": TEST_USER_ID})
response = requests.get(
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}",
    headers={"X-User-ID": TEST_USER_ID}
)
print_response("GET /newspapers/{newspaper_id}", response)

# 2. GET /newspapers (without filters)
print("\n2. Testing GET /newspapers (no filters)")
print_curl_command("GET", f"{BASE_URL}/newspapers", headers={"X-User-ID": TEST_USER_ID})
response = requests.get(
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID}
)
print_response("GET /newspapers (no filters)", response)

# 3. GET /newspapers (with date filter)
print("\n3. Testing GET /newspapers (with date filter)")
print_curl_command("GET", f"{BASE_URL}/newspapers", headers={"X-User-ID": TEST_USER_ID}, params={"date": "25/01/2025"})
response = requests.get(
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID},
    params={"date": "25/01/2025"}
)
print_response("GET /newspapers (with date filter)", response)

# 4. GET /newspapers (with pagination)
print("\n4. Testing GET /newspapers (with pagination)")
print_curl_command("GET", f"{BASE_URL}/newspapers", headers={"X-User-ID": TEST_USER_ID}, params={"page_limit": 5})
response = requests.get(
    f"{BASE_URL}/newspapers",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5, "starting_after": None}
)
print_response("GET /newspapers (with pagination)", response)


# ============================================================================
# GENERATED CONTENT CONTROLLER ENDPOINTS
# ============================================================================

print("\n" + "="*60)
print("TESTING GENERATED CONTENT CONTROLLER ENDPOINTS")
print("="*60)

# 5. POST /generated_content/{generated_content_id}/user_interaction
print("\n5. Testing POST /generated_content/{generated_content_id}/user_interaction")
json_body = {
    "user_id": TEST_USER_ID,
    "interaction_type": "LIKE",
    "metadata": {"source": "test"}
}
print_curl_command("POST", f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction", json_data=json_body)
response = requests.post(
    f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction",
    json=json_body
)
print_response("POST /generated_content/{id}/user_interaction (LIKE)", response)

# Try different interaction types
for interaction_type in ["DISLIKE", "SAVED", "REPORT"]:
    print(f"\n5.{interaction_type}. Testing POST with {interaction_type}")
    json_body = {
        "user_id": TEST_USER_ID,
        "interaction_type": interaction_type,
        "metadata": {"source": "test"}
    }
    print_curl_command("POST", f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction", json_data=json_body)
    response = requests.post(
        f"{BASE_URL}/generated_content/{TEST_GENERATED_CONTENT_ID}/user_interaction",
        json=json_body
    )
    print_response(f"POST /generated_content/{{id}}/user_interaction ({interaction_type})", response)

# 6. GET /list_user_interactions_for_content/{content_id}
print("\n6. Testing GET /list_user_interactions_for_content/{content_id}")
print_curl_command("GET", f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}")
response = requests.get(
    f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}"
)
print_response("GET /list_user_interactions_for_content/{content_id}", response)

# 7. GET /list_user_interactions_for_content/{content_id} (with pagination)
print("\n7. Testing GET /list_user_interactions_for_content/{content_id} (with pagination)")
print_curl_command("GET", f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}", params={"page_limit": 5})
response = requests.get(
    f"{BASE_URL}/list_user_interactions_for_content/{TEST_GENERATED_CONTENT_ID}",
    params={"page_limit": 5, "starting_after": None}
)
print_response("GET /list_user_interactions_for_content/{content_id} (pagination)", response)

# 8. GET /list_user_interactions (no filters)
print("\n8. Testing GET /list_user_interactions (no filters)")
print_curl_command("GET", f"{BASE_URL}/list_user_interactions", headers={"X-User-ID": TEST_USER_ID})
response = requests.get(
    f"{BASE_URL}/list_user_interactions",
    headers={"X-User-ID": TEST_USER_ID}
)
print_response("GET /list_user_interactions (no filters)", response)

# 9. GET /list_user_interactions (with interaction_type filter)
print("\n9. Testing GET /list_user_interactions (with interaction_type filter)")
for interaction_type in ["LIKE", "DISLIKE", "SAVED", "REPORT"]:
    print(f"\n9.{interaction_type}. Testing with filter: {interaction_type}")
    print_curl_command("GET", f"{BASE_URL}/list_user_interactions", headers={"X-User-ID": TEST_USER_ID}, params={"interaction_type": interaction_type})
    response = requests.get(
        f"{BASE_URL}/list_user_interactions",
        headers={"X-User-ID": TEST_USER_ID},
        params={"interaction_type": interaction_type}
    )
    print_response(f"GET /list_user_interactions (filter: {interaction_type})", response)

# 10. GET /list_user_interactions (with pagination)
print("\n10. Testing GET /list_user_interactions (with pagination)")
print_curl_command("GET", f"{BASE_URL}/list_user_interactions", headers={"X-User-ID": TEST_USER_ID}, params={"page_limit": 5})
response = requests.get(
    f"{BASE_URL}/list_user_interactions",
    headers={"X-User-ID": TEST_USER_ID},
    params={"page_limit": 5, "starting_after": None}
)
print_response("GET /list_user_interactions (with pagination)", response)

# 11. GET /generated_content/{content_id} (uses external_id)
print("\n11. Testing GET /generated_content/{content_id} (uses external_id)")
print_curl_command("GET", f"{BASE_URL}/generated_content/{TEST_CONTENT_EXTERNAL_ID}")
response = requests.get(
    f"{BASE_URL}/generated_content/{TEST_CONTENT_EXTERNAL_ID}"
)
print_response("GET /generated_content/{content_id}", response)
# Note: Use the 'id' field from this response as TEST_GENERATED_CONTENT_ID for interaction endpoints

# 12. GET /newspapers/{newspaper_id}/generated_content
print("\n12. Testing GET /newspapers/{newspaper_id}/generated_content")
print_curl_command("GET", f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content")
response = requests.get(
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content"
)
print_response("GET /newspapers/{newspaper_id}/generated_content", response)

# 13. GET /newspapers/{newspaper_id}/generated_content (with pagination)
print("\n13. Testing GET /newspapers/{newspaper_id}/generated_content (with pagination)")
print_curl_command("GET", f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content", params={"page_limit": 5})
response = requests.get(
    f"{BASE_URL}/newspapers/{TEST_NEWSPAPER_ID}/generated_content",
    params={"page_limit": 5, "starting_after": None}
)
print_response("GET /newspapers/{newspaper_id}/generated_content (pagination)", response)


# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)
print("\nNote: Update TEST_NEWSPAPER_ID, TEST_CONTENT_EXTERNAL_ID, and TEST_GENERATED_CONTENT_ID")
print("at the top of this script with actual IDs from your database for accurate testing.")
print("\nImportant:")
print("- TEST_CONTENT_EXTERNAL_ID: External ID (e.g., YouTube video ID)")
print("- TEST_GENERATED_CONTENT_ID: MongoDB internal _id (get from GET /generated_content/{external_id} response 'id' field)")
print("- Interaction endpoints now use MongoDB internal _id, not external_id")

