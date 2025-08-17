"""
User service client for newspaper service.
"""

import logging
from typing import Dict, List, Optional

import httpx

from user_service.models.user import User


class UserServiceClient:
    """Client for communicating with the user service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def get_user(self, user_id: str) -> Optional[User]:
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
