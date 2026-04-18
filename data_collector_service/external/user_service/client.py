from typing import Optional

import httpx
from injector import inject

from data_collector_service.config.config import Config
from data_collector_service.infra.dependency_injection.injectable import \
    injectable
from user_service.models.user import User


@injectable()
class UserServiceClient:
    """Client for interacting with the user service."""

    @inject
    def __init__(self, config: Config):
        if config is None:
            config = Config()
        self.base_url = config.user_service_url
        self.timeout = config.user_service_timeout

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Fetch user data from the user service.

        Args:
            user_id: The unique identifier of the user

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
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
