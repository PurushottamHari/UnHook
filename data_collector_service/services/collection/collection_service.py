from datetime import datetime
from injector import inject

from user_service.models.user import User
from user_service.models.enums import Weekday

from data_collector_service.exceptions.user_exception import user_exception
from data_collector_service.external.user_service.client import UserServiceClient
from data_collector_service.repositories.user_collected_content_repository import (
    UserCollectedContentRepository,
)
from data_collector_service.service_context import DataCollectorServiceContext

from .collectors.youtube.discover import YouTubeDiscoverCollector
from .collectors.youtube.static import YouTubeStaticCollector

from data_collector_service.infra.dependency_injection.injectable import injectable


@injectable()
class CollectionService:
    """Service responsible for orchestrating data collection for all users."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        service_context: DataCollectorServiceContext,
        youtube_discover_collector: YouTubeDiscoverCollector,
        youtube_static_collector: YouTubeStaticCollector,
    ):
        """
        Initialize the collection service.

        Args:
            user_service_client: Client for interacting with the user service
            service_context: Context for maintaining service state and metrics
        """
        self.user_service_client = user_service_client
        self.service_context = service_context

        self.youtube_discover_collector = youtube_discover_collector
        self.youtube_static_collector = youtube_static_collector

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
        try:
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

            # Complete metrics collection
            if self.service_context.get_metrics_processor():
                self.service_context.get_metrics_processor().complete(success=True)
                print(
                    f"✅ Data collection completed. Total videos: {self.service_context.get_metrics_processor().get_total_videos()}"
                )

        except Exception as e:
            # Complete metrics collection with error
            if self.service_context.get_metrics_processor():
                self.service_context.get_metrics_processor().complete(
                    success=False, error_message=str(e)
                )
            raise
