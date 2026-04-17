import redis.asyncio as redis
from injector import inject
from commons.messaging import MessageProducer, Command, Event
from data_collector_service.config.config import Config
from data_collector_service.infra.dependency_injection.injectable import injectable


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

    async def close(self) -> None:
        """Close the Redis client connection."""
        await self.redis_client.close()
