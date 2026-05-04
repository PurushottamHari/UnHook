from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from commons.messaging.models import BaseMessage, Command, Event


class MessageConsumer(ABC):
    """
    Abstract base class for consuming messages asynchronously.
    Implementations will manage the connection to the broker,
    polling/listening mechanics, and dispatching to registered handlers.
    """

    @abstractmethod
    def register_event_handler(
        self, topic: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None:
        """
        Register an asynchronous handler for a specific event topic.

        Args:
            topic: The topic/channel to listen on.
            handler: An async function accepting a single Event argument.
        """
        pass

    @abstractmethod
    def register_command_handler(
        self, topic: str, handler: Callable[[Command], Awaitable[None]]
    ) -> None:
        """
        Register an asynchronous handler for a specific command topic/queue.

        Args:
            topic: The topic/queue to listen on.
            handler: An async function accepting a single Command argument.
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        Start consuming messages from the broker.
        This method is expected to block and run continuously, listening for incoming
        events/commands and routing them to the appropriate handlers.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Gracefully stop the consumer, closing connections and finishing
        currently processing messages.
        """
        pass

    @abstractmethod
    async def acknowledge(self, message: BaseMessage) -> None:
        """
        Acknowledge a message as processed.
        Uses the metadata attached to the message to identify it in the broker.
        """
        pass
