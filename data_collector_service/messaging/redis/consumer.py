import asyncio
import json
from typing import Awaitable, Callable, Dict, List
from injector import inject

import redis.asyncio as redis
from commons.messaging import MessageConsumer, Command, Event
from data_collector_service.config.config import Config
from data_collector_service.infra.dependency_injection.injectable import injectable


@injectable()
class RedisMessageConsumer(MessageConsumer):
    """
    Redis implementation of the MessageConsumer abstraction.
    Listens to Redis channels for events and Redis lists for commands.
    """

    @inject
    def __init__(self, config: Config):
        """
        Initialize the Redis consumer.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database index
        """
        self.host = config.redis_host
        self.port = config.redis_port
        self.db = config.redis_db
        self.redis_client = redis.Redis(
            host=self.host, port=self.port, db=self.db, decode_responses=True
        )
        self.event_handlers: Dict[str, List[Callable[[Event], Awaitable[None]]]] = {}
        self.command_handlers: Dict[str, List[Callable[[Command], Awaitable[None]]]] = (
            {}
        )
        self._running = False

    def register_event_handler(
        self, topic: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None:
        """Register an async handler for a specific event topic (channel)."""
        if topic not in self.event_handlers:
            self.event_handlers[topic] = []
        self.event_handlers[topic].append(handler)
        print(f"✅ [Redis] Registered event handler for topic '{topic}'")

    def register_command_handler(
        self, topic: str, handler: Callable[[Command], Awaitable[None]]
    ) -> None:
        """Register an async handler for a specific command topic (queue)."""
        if topic not in self.command_handlers:
            self.command_handlers[topic] = []
        self.command_handlers[topic].append(handler)
        print(f"✅ [Redis] Registered command handler for topic '{topic}'")

    async def start(self) -> None:
        """Start the Redis consumer loop."""
        self._running = True
        print(f"🚀 [Redis] Consumer starting on {self.host}:{self.port}...")

        # Create tasks for events and commands
        tasks = []
        if self.event_handlers:
            tasks.append(self._listen_for_events())
        if self.command_handlers:
            tasks.append(self._listen_for_commands())

        if not tasks:
            print("⚠️ [Redis] No handlers registered. Consumer exiting.")
            return

        await asyncio.gather(*tasks)

    async def stop(self) -> None:
        """Stop the consumer loop."""
        self._running = False
        await self.redis_client.close()
        print("🛑 [Redis] Consumer stopped.")

    async def _listen_for_events(self) -> None:
        """Listen for events using Pub/Sub."""
        pubsub = self.redis_client.pubsub()
        topics = list(self.event_handlers.keys())
        await pubsub.subscribe(*topics)
        print(f"📻 [Redis] Subscribed to event topics: {topics}")

        while self._running:
            try:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message["type"] == "message":
                    topic = message["channel"]
                    data = json.loads(message["data"])
                    event = Event(**data)

                    # Process events (broadcast to all registered handlers for this topic)
                    handlers = self.event_handlers.get(topic, [])
                    for handler in handlers:
                        try:
                            await handler(event)
                        except Exception as e:
                            print(
                                f"❌ [Redis] Error in event handler for topic '{topic}': {e}"
                            )
            except Exception as e:
                print(f"❌ [Redis] Error listening for events: {e}")
                await asyncio.sleep(1)

    async def _listen_for_commands(self) -> None:
        """Listen for commands using BRPOP (blocking list pop)."""
        queues = list(self.command_handlers.keys())
        print(f"📥 [Redis] Listening for commands on queues: {queues}")

        while self._running:
            try:
                # BRPOP returns (queue_name, data)
                result = await self.redis_client.brpop(queues, timeout=1)
                if result:
                    queue_name, data = result
                    data_dict = json.loads(data)
                    command = Command(**data_dict)

                    print(
                        f"📥 [Redis] Received command '{command.action_name}' from queue '{queue_name}'"
                    )

                    # Process command handlers sequentially as requested
                    handlers = self.command_handlers.get(queue_name, [])
                    for handler in handlers:
                        try:
                            await handler(command)
                        except Exception as e:
                            print(
                                f"❌ [Redis] Error in command handler for queue '{queue_name}': {e}"
                            )
            except Exception as e:
                print(f"❌ [Redis] Error listening for commands: {e}")
                await asyncio.sleep(1)
