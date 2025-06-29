from typing import Optional

import httpx

from user_service.models.user import User


class UserServiceClient:
    """Client for interacting with the user service."""

    def __init__(self):
        self.base_url = "http://localhost:8000"

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Fetch user data from the user service.

        Args:
            user_id: The unique identifier of the user

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/users/{user_id}",
                    headers={"accept": "application/json"},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return User(**response.json())

        except (ValueError, httpx.HTTPError):
            # Handle invalid UUID format or HTTP errors
            return None
