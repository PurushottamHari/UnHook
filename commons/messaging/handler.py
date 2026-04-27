import time

from injector import inject

from .config import BaseMessagingConfig
from .consumer import MessageConsumer
from .exceptions import RescheduleMessageException
from .models import MessageAttempt
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
            command_topic, self._wrap_handler(self.command_router.handle)
        )
        print(
            f"🛠️ [BaseMessagingHandler] Command router registered to: {command_topic}"
        )

        # 2. Register Event Router for each specified interested event
        interested_events = self.config.interested_events
        for event in interested_events:
            self.consumer.register_event_handler(
                event.topic, self._wrap_handler(self.event_router.handle)
            )
            print(
                f"🛠️ [BaseMessagingHandler] Event router registered to: {event.topic}"
            )

    def _wrap_handler(self, handler):
        """Wraps a handler with robust error handling and retry logic."""

        async def wrapper(message):
            await self._handle_message(message, handler)

        return wrapper

    async def _handle_message(self, message, handler):
        """Executes a handler and manages acknowledgment or failure."""
        try:
            await handler(message)
            await self.consumer.acknowledge(message)
        except Exception as e:
            await self._orchestrate_failure(message, e)

    async def _orchestrate_failure(self, message, exception):
        """Decides whether to retry or move a failed message to DLQ."""
        # 1. Update context with attempt metadata
        attempt = MessageAttempt(
            failed_error_code=type(exception).__name__,
            failed_error_message=str(exception),
        )
        message.context.attempts.append(attempt)

        # 2. Configuration
        current_retry_count = message.context.retry_count
        max_retries = 3  # Default: 4 attempts total (0, 1, 2, 3)
        delay_ms = 0

        if isinstance(exception, RescheduleMessageException):
            delay_ms = exception.delay_ms
            max_retries = exception.max_retries
        else:
            # Standard delays: 2m, 10m, 15m
            delays_ms = [120000, 600000, 900000]
            if current_retry_count < len(delays_ms):
                delay_ms = delays_ms[current_retry_count]

        # 3. Decision and Execution
        if current_retry_count < max_retries:
            # Retry Path
            message.context.retry_count += 1
            print(
                f"🔄 [BaseMessagingHandler] Retrying message {message.message_id} "
                f"(Attempt {message.context.retry_count}) in {delay_ms}ms..."
            )
            await self.producer.schedule_message(message, delay_ms)
        else:
            # DLQ Path
            print(
                f"💀 [BaseMessagingHandler] Message {message.message_id} failed after "
                f"{current_retry_count} retries. Moving to DLQ."
            )
            await self.producer.send_to_dlq(
                self.config.service_name, message, str(exception)
            )

        # Always acknowledge the original message as it's been handled (moved or rescheduled)
        await self.consumer.acknowledge(message)

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
