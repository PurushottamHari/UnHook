from abc import ABC, abstractmethod
from typing import Any, Dict

from commons.messaging.models import Command, Event


class MessageProducer(ABC):
    """
    Abstract base class for producing messages.
    Implementations (Kafka, Redis, RabbitMQ, etc.) will subclass this
    and provide the specific transport logic.
    """

    @abstractmethod
    async def publish_event(self, topic: str, event: Event) -> None:
        """
        Publish an event to a topic.

        Args:
            topic: The destination topic (or channel/exchange depending on broker).
            event: The fully constructed Event model.
        """
        pass

    @abstractmethod
    async def send_command(self, topic: str, command: Command) -> None:
        """
        Send a command to a specific service's topic or queue.

        Args:
            topic: The destination topic/queue for the command.
            command: The fully constructed Command model.
        """
        pass
