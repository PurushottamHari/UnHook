import asyncio
from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.config.config import Config
from data_collector_service.messaging.redis.consumer import \
    RedisMessageConsumer
from data_collector_service.messaging.redis.producer import \
    RedisMessageProducer
from data_collector_service.messaging.routers.command_router import \
    CommandRouter
from data_collector_service.messaging.routers.event_router import EventRouter
from data_collector_service.services.collection.collection_service import \
    CollectionService
from data_collector_service.services.rejection.reject_content_service import \
    RejectContentService


@injectable()
class MessagingHandler:
    """Orchestrates the lifecycle and registration of the messaging system."""

    @inject
    def __init__(
        self,
        config: Config,
        producer: RedisMessageProducer,
        consumer: RedisMessageConsumer,
        command_router: CommandRouter,
        event_router: EventRouter,
    ):
        """
        Initialize the messaging handler.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize producer and consumer
        self.producer = producer
        self.consumer = consumer
        self.command_router = command_router
        self.event_router = event_router

    def _register_handlers(self):
        """Setup routers and register them with the consumer."""
        print(f"🚀 Registering Command and Event handlers...")

        # Register command router
        command_topic = self.config.messaging_command_topic
        self.consumer.register_command_handler(
            command_topic, self.command_router.handle
        )
        print(f"🛠️ [Handlers] Command router registered to topic: {command_topic}")

        # List of event topics this service should listen to
        event_topics: List[str] = [
            # "user_service.events",
        ]

        for topic in event_topics:
            self.consumer.register_event_handler(topic, self.event_router.handle)

        if event_topics:
            print(
                f"🛠️ [Handlers] Event router registered for {len(event_topics)} topics."
            )

    async def start(self):
        """Start the message consumer and handle lifecycle."""
        self._register_handlers()
        print(f"✅ Starting Data Collector Service in Consumer Mode...")
        try:
            await self.consumer.start()
        except asyncio.CancelledError:
            await self.stop()
        except Exception as e:
            print(f"❌ MessagingHandler encountered an error: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Gracefully shutdown the producer and consumer."""
        print("🛑 Stopping MessagingHandler...")
        await self.consumer.stop()
        await self.producer.close()
