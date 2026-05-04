from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from commons.messaging.models import BaseMessage, Command, Event


class MessageProducer(ABC):
    """
    Abstract base class for producing messages.
    Implementations (Kafka, Redis, RabbitMQ, etc.) will subclass this
    and provide the specific transport logic.
    """

    @abstractmethod
    async def publish_event(self, event: Event) -> None:
        """
        Publish an event.
        Uses event.topic for routing.

        Args:
            event: The fully constructed Event model.
        """
        pass

    @abstractmethod
    async def publish_events(self, events: list[Event]) -> None:
        """
        Publish multiple events in batch.
        Uses event.topic for each event's routing.

        Args:
            events: A list of fully constructed Event models.
        """
        pass

    @abstractmethod
    async def send_command(self, command: Command) -> None:
        """
        Send a command to a specific service's topic or queue.
        Uses command.topic for routing.

        Args:
            command: The fully constructed Command model.
        """
        pass

    @abstractmethod
    async def send_commands(self, commands: list[Command]) -> None:
        """
        Send multiple commands in batch.
        Uses command.topic for each command's routing.

        Args:
            commands: A list of fully constructed Command models.
        """
        pass

    @abstractmethod
    async def schedule_command(self, command: Command, schedule_at: datetime) -> None:
        """
        Schedule a command to be executed at a specific time.
        Uses command.topic for routing.

        Args:
            command: The fully constructed Command model.
            schedule_at: The time at which the command should be sent to the active queue.
        """
        pass

    @abstractmethod
    async def schedule_message(self, message: BaseMessage, delay_ms: int) -> None:
        """
        Schedule a message to be processed after a specific delay.
        Uses message.topic for routing.
        """
        pass

    @abstractmethod
    async def send_to_dlq(
        self, service_name: str, message: BaseMessage, reason: str
    ) -> None:
        """
        Send a message to the Dead Letter Queue.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the producer connection.
        """
        pass
