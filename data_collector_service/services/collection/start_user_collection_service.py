import logging
from datetime import datetime

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.config.config import Config
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.messaging.models.commands import (
    CollectYouTubeChannelForUserCommand, CollectYouTubeChannelForUserPayload)
from data_collector_service.messaging.redis.producer import \
    RedisMessageProducer
from user_service.models.enums import Weekday

logger = logging.getLogger(__name__)


@injectable()
class StartUserCollectionService:
    """Service responsible for orchestrating the start of data collection by enqueuing granular commands."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        message_producer: RedisMessageProducer,
        config: Config,
    ):
        """
        Initialize the service.

        Args:
            user_service_client: Client to interact with user service
            message_producer: Producer to send commands to the queue
            config: Application configuration
        """
        self.user_service_client = user_service_client
        self.message_producer = message_producer
        self.config = config

    def _should_collect_discover(self, user) -> bool:
        """Check if discover collection should be performed for the user today."""
        today = Weekday(datetime.utcnow().strftime("%A").upper())
        return today in user.manual_configs.youtube.discover_on

    async def start_collection(self, user_id: str) -> None:
        """
        Triggers collection for a user by breaking it down into channel-specific commands.

        Args:
            user_id: The unique identifier of the user
        """
        try:
            user = await self.user_service_client.get_user(user_id)
            if not user:
                logger.error(f"User {user_id} not found.")
                return

            if not getattr(user.manual_configs, "youtube", None):
                logger.info(f"No YouTube configuration found for user {user_id}")
                return

            youtube_config = user.manual_configs.youtube
            commands_to_send = []

            # 1. Handle Discover Collection if applicable
            if self._should_collect_discover(user):
                logger.info(f"Discover not implemented yet.....")
                # Placeholder for when discover is implemented:
                # discover_payload = CollectYouTubeChannelForUserPayload(...)
                # commands_to_send.append(CollectYouTubeChannelForUserCommand(payload=discover_payload))

            # 2. Handle Static Collection for each channel
            for channel in youtube_config.channels:
                channel_id = channel.channel_id
                max_videos = channel.max_videos_daily

                # TODO: Puru locks can be considered here at a later stage to deduplicate same channel across users.

                static_payload = CollectYouTubeChannelForUserPayload(
                    user_id=user_id,
                    channel_id=channel_id,
                    max_videos=max_videos,
                    collection_type="static",
                )
                static_command = CollectYouTubeChannelForUserCommand(
                    payload=static_payload
                )
                commands_to_send.append(static_command)

            # 3. Batch publish all commands
            if commands_to_send:
                await self.message_producer.send_commands(commands_to_send)
                logger.info(
                    f"✅ Enqueued {len(commands_to_send)} collection commands for user {user_id}"
                )
            else:
                logger.info(f"No collection tasks generated for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to start collection for user {user_id}: {e}")
            raise
