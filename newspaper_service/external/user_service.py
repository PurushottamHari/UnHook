"""
User service client for newspaper service.
"""

import logging
from typing import Dict, List, Optional

import httpx
from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from newspaper_service.config.config import Config
from user_service.models.user import User


@injectable()
class UserServiceClient:
    """Client for communicating with the user service."""

    @inject
    def __init__(self, config: Config):
        if config is None:
            config = Config()
        self.base_url = config.user_service_url
        self.timeout = config.user_service_timeout
        self.logger = logging.getLogger(__name__)
        self._verify_connectivity()

    def _verify_connectivity(self):
        """Verify connectivity to the user service on startup."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/health")
                if response.status_code != 200:
                    raise Exception(
                        f"User service health check failed with status {response.status_code}"
                    )
            self.logger.info(f"✅ [UserServiceClient] Connected to {self.base_url}")
        except Exception as e:
            self.logger.error(
                f"❌ [UserServiceClient] Failed to connect to {self.base_url}: {e}"
            )

    def get_user(self, user_id: str) -> Optional[User]:
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
