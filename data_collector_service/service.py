from datetime import datetime
from typing import Optional

from data_collector_service.models.user_collected_content import ContentType
from user_service.models.enums import Weekday
from user_service.models.user import User

from .collectors.youtube.discover import YouTubeDiscoverCollector
from .collectors.youtube.static import YouTubeStaticCollector
from .exceptions.user_exception import user_exception
from .external.user_service.client import UserServiceClient
from .repositories.mongodb.config.database import MongoDB
from .repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository


class DataCollectorService:
    """Service responsible for orchestrating data collection for all users."""

    def __init__(self, user_service_client: UserServiceClient):
        """
        Initialize the data collector service.

        Args:
            user_service_client: Client for interacting with the user service
        """
        self.user_service_client = user_service_client
        # Initialize MongoDB connection
        MongoDB.connect_to_database()
        # Create MongoDB repository instance
        user_repository = MongoDBUserCollectedContentRepository()
        # Pass the repository to the collectors
        self.youtube_discover_collector = YouTubeDiscoverCollector(user_repository)
        self.youtube_static_collector = YouTubeStaticCollector(user_repository)

    def _should_collect_discover(self, user: User) -> bool:
        """
        Check if discover collection should be performed for the user today.

        Args:
            user: User object containing user configuration and preferences

        Returns:
            bool: True if discover collection should be performed today
        """
        today = Weekday(datetime.utcnow().strftime("%A").upper())
        return today in user.manual_configs.youtube.discover_on

    def collect_for_user(self, user_id: str) -> None:
        """
        Collect data for a single user based on their configuration.

        Args:
            user_id: The unique identifier of the user
        """
        user = self.user_service_client.get_user(user_id)
        if not user:
            raise user_exception(user_id)

        # Only proceed if user.manual_configs.youtube exists
        if getattr(user.manual_configs, "youtube", None):
            # Check and perform discover collection if needed
            if self._should_collect_discover(user):
                self.youtube_discover_collector.collect(user)

            # Perform static collection if needed
            self.youtube_static_collector.collect(user)


if __name__ == "__main__":
    user_service_client = UserServiceClient()
    data_collector_service = DataCollectorService(user_service_client)
    data_collector_service.collect_for_user(
        user_id="607d95f0-47ef-444c-89d2-d05f257d1265"
    )
