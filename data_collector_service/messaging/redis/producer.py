import time
from datetime import datetime

import redis.asyncio as redis
from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseMessage, Command, Event, MessageProducer
from data_collector_service.config.config import Config


@injectable()
class RedisMessageProducer(MessageProducer):
    """
    Redis implementation of the MessageProducer abstraction.
    Uses Redis Pub/Sub for events and Lists for commands.
    """

    @inject
    def __init__(self, config: Config):
        """
        Initialize the Redis producer.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database index
        """
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            decode_responses=True,
        )

    async def publish_event(self, event: Event) -> None:
        """
        Publish an event to a Redis Stream.

        Args:
            event: The Event object to publish
        """
        message_json = event.model_dump_json()
        await self.redis_client.xadd(event.topic, {"payload": message_json})
        print(
            f"📡 [Redis] Event published to stream '{event.topic}': {event.event_type}"
        )

    async def send_command(self, command: Command) -> None:
        """
        Send a command to a Redis Stream.

        Args:
            command: The Command object to send
        """
        message_json = command.model_dump_json()
        await self.redis_client.xadd(command.topic, {"payload": message_json})
        print(
            f"📤 [Redis] Command sent to stream '{command.topic}': {command.action_name}"
        )

    async def send_commands(self, commands: list[Command]) -> None:
        """
        Send multiple commands to Redis Streams.
        """
        if not commands:
            return

        async with self.redis_client.pipeline() as pipe:
            for command in commands:
                message_json = command.model_dump_json()
                pipe.xadd(command.topic, {"payload": message_json})
            await pipe.execute()

        print(f"📤 [Redis] {len(commands)} commands batch sent.")

    async def schedule_command(self, command: Command, schedule_at: datetime) -> None:
        """
        Schedule a command to be added to a Redis Stream at a specific time.

        Args:
            command: The Command object to schedule.
            schedule_at: The datetime at which to send the command.
        """
        message_json = command.model_dump_json()
        timestamp = schedule_at.timestamp()

        # We use a Sorted Set for scheduling: ZADD scheduled:{topic} {timestamp} {payload}
        scheduled_key = f"scheduled:{command.topic}"
        await self.redis_client.zadd(scheduled_key, {message_json: timestamp})

        print(
            f"⏰ [Redis] Command '{command.action_name}' scheduled for {schedule_at} on topic '{command.topic}'"
        )

    async def schedule_message(self, message: BaseMessage, delay_ms: int) -> None:
        """
        Schedule a message to be processed after a specific delay.
        """
        message_json = message.model_dump_json()
        timestamp = time.time() + (delay_ms / 1000)
        scheduled_key = f"scheduled:{message.topic}"
        await self.redis_client.zadd(scheduled_key, {message_json: timestamp})
        print(
            f"⏰ [Redis] Message {message.message_id} scheduled for topic '{message.topic}' in {delay_ms}ms"
        )

    async def send_to_dlq(
        self, service_name: str, message: BaseMessage, reason: str
    ) -> None:
        """
        Send a message to the Dead Letter Queue.
        """
        dlq_stream = f"{service_name}:dead_letter_queue"

        # Save original topic and temporarily update it for serialization
        original_topic = message.topic
        message.topic = dlq_stream

        message_json = message.model_dump_json()

        # Restore original topic so subsequent local calls (like acknowledge) work
        message.topic = original_topic

        await self.redis_client.xadd(
            dlq_stream,
            {
                "payload": message_json,
                "reason": reason,
                "original_message_id": str(message.message_id),
            },
        )
        print(f"💀 [Redis] Message {message.message_id} moved to DLQ: {dlq_stream}")

    async def close(self) -> None:
        """Close the Redis client connection."""
        await self.redis_client.close()
