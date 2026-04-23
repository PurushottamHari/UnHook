import logging
from typing import Optional

import httpx
from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_processing_service.config.config import Config
from user_service.models.user import User

logger = logging.getLogger(__name__)


@injectable()
class UserServiceClient:
    """Client for interacting with the user service."""

    @inject
    def __init__(self, config: Config):
        self.base_url = config.user_service_url
        self.timeout = config.user_service_timeout

    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Fetch user data from the user service asynchronously.

        Args:
            user_id: The unique identifier of the user

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/users/{user_id}",
                    headers={"accept": "application/json"},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return User(**response.json())

        except httpx.HTTPError as e:
            logger.error(
                f"❌ [UserServiceClient] HTTP error fetching user {user_id}: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"❌ [UserServiceClient] Unexpected error fetching user {user_id}: {e}"
            )
            return None
