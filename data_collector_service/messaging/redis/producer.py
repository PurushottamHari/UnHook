from datetime import datetime

import redis.asyncio as redis
from injector import inject

from commons.messaging import Command, Event, MessageProducer
from data_collector_service.config.config import Config
from data_collector_service.infra.dependency_injection.injectable import \
    injectable


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

    async def publish_event(self, topic: str, event: Event) -> None:
        """
        Publish an event to a Redis channel.

        Args:
            topic: The Redis channel to publish to
            event: The Event object to publish
        """
        message_json = event.model_dump_json()
        await self.redis_client.publish(topic, message_json)
        print(f"📡 [Redis] Event published to topic '{topic}': {event.event_type}")

    async def send_command(self, topic: str, command: Command) -> None:
        """
        Send a command to a Redis list (queue).

        Args:
            topic: The Redis list key to push the command to
            command: The Command object to send
        """
        message_json = command.model_dump_json()
        await self.redis_client.lpush(topic, message_json)
        print(f"📤 [Redis] Command sent to queue '{topic}': {command.action_name}")

    async def send_commands(self, topic: str, commands: list[Command]) -> None:
        """
        Send multiple commands to a Redis list (queue) in one batch.

        Args:
            topic: The Redis list key to push the commands to
            commands: A list of Command objects to send
        """
        if not commands:
            return

        message_jsons = [command.model_dump_json() for command in commands]
        # LPUSH supports multiple values: LPUSH key value1 value2 ...
        await self.redis_client.lpush(topic, *message_jsons)
        print(
            f"📤 [Redis] {len(commands)} commands batch sent to queue '{topic}': {[c.action_name for c in commands][:3]}..."
        )

    async def schedule_command(
        self, topic: str, command: Command, schedule_at: datetime
    ) -> None:
        """
        Schedule a command to be added to a Redis queue at a specific time.

        Args:
            topic: The destination queue topic.
            command: The Command object to schedule.
            schedule_at: The datetime at which to send the command.
        """
        message_json = command.model_dump_json()
        timestamp = schedule_at.timestamp()

        # We use a Sorted Set for scheduling: ZADD scheduled:{topic} {timestamp} {payload}
        scheduled_key = f"scheduled:{topic}"
        await self.redis_client.zadd(scheduled_key, {message_json: timestamp})

        print(
            f"⏰ [Redis] Command '{command.action_name}' scheduled for {schedule_at} on topic '{topic}'"
        )

    async def close(self) -> None:
        """Close the Redis client connection."""
        await self.redis_client.close()
