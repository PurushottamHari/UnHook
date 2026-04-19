from abc import ABC, abstractmethod
from typing import List

from .consumer import MessageConsumer
from .producer import MessageProducer
from .router import BaseCommandRouter, BaseEventRouter


class BaseMessagingHandler(ABC):
    """
    Abstract base class for orchestrating the messaging lifecycle.
    Manages registration of routers and start/stop operations.
    """

    def __init__(
        self,
        consumer: MessageConsumer,
        producer: MessageProducer,
        command_router: BaseCommandRouter,
        event_router: BaseEventRouter,
        service_name: str,
    ):
        self.consumer = consumer
        self.producer = producer
        self.command_router = command_router
        self.event_router = event_router
        self.service_name = service_name

    def _register_handlers(self):
        """Setup routers and register them with the consumer."""
        # 1. Register Command Router
        command_topic = f"{self.service_name}.commands"
        self.consumer.register_command_handler(
            command_topic, self.command_router.handle
        )
        print(
            f"🛠️ [BaseMessagingHandler] Command router registered to: {command_topic}"
        )

        # 2. Register Event Router for each specified topic
        event_topics = self.get_event_topics()
        for topic in event_topics:
            self.consumer.register_event_handler(topic, self.event_router.handle)

        if event_topics:
            print(
                f"🛠️ [BaseMessagingHandler] Event router registered for {len(event_topics)} topics: {event_topics}"
            )

    @abstractmethod
    def get_event_topics(self) -> List[str]:
        """Must be implemented by subclasses to specify event topics to subscribe to."""
        pass

    async def start(self):
        """Start the message consumer and handle lifecycle."""
        self._register_handlers()
        print(f"🚀 Starting {self.service_name} messaging consumer...")
        await self.consumer.start()

    async def stop(self):
        """Gracefully shutdown the producer and consumer."""
        print(f"🛑 Stopping {self.service_name} messaging components...")
        await self.consumer.stop()
        await self.producer.close()
