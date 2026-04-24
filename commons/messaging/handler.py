from injector import inject

from .config import BaseMessagingConfig
from .consumer import MessageConsumer
from .producer import MessageProducer
from .router import BaseCommandRouter, BaseEventRouter


class BaseMessagingHandler:
    """
    Concrete engine for orchestrating the messaging lifecycle.
    Manages registration of routers and start/stop operations.
    """

    @inject
    def __init__(
        self,
        consumer: MessageConsumer,
        producer: MessageProducer,
        command_router: BaseCommandRouter,
        event_router: BaseEventRouter,
        config: BaseMessagingConfig,
    ):
        self.consumer = consumer
        self.producer = producer
        self.command_router = command_router
        self.event_router = event_router
        self.config = config

    def _register_handlers(self):
        """Setup routers and register them with the consumer."""
        # 1. Register Command Router
        command_topic = f"{self.config.service_name}.commands"
        self.consumer.register_command_handler(
            command_topic, self.command_router.handle
        )
        print(
            f"🛠️ [BaseMessagingHandler] Command router registered to: {command_topic}"
        )

        # 2. Register Event Router for each specified interested event
        interested_events = self.config.interested_events
        for event in interested_events:
            self.consumer.register_event_handler(event.topic, self.event_router.handle)
            print(
                f"🛠️ [BaseMessagingHandler] Event router registered to: {event.topic}"
            )

    async def start(self):
        """Start the message consumer and handle lifecycle."""
        self._register_handlers()
        print(f"🚀 Starting {self.config.service_name} messaging consumer...")
        await self.consumer.start()

    async def stop(self):
        """Gracefully shutdown the producer and consumer."""
        print(f"🛑 Stopping {self.config.service_name} messaging components...")
        await self.consumer.stop()
        await self.producer.close()
