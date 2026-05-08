import asyncio
import json
import socket
import time
from enum import Enum
from typing import Awaitable, Callable, Dict, List

from injector import inject
from redis import asyncio as aioredis
from redis.exceptions import ResponseError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseMessage, Command, Event, MessageConsumer
from newspaper_service.config.config import Config


class MessageType(Enum):
    EVENT = "events"
    COMMAND = "commands"


@injectable()
class RedisMessageConsumer(MessageConsumer):
    @inject
    def __init__(self, config: Config):
        self.config = config
        self.redis_client = aioredis.from_url(config.redis_url, decode_responses=True)
        self.event_handlers: Dict[str, List[Callable[[Event], Awaitable[None]]]] = {}
        self.command_handlers: Dict[str, List[Callable[[Command], Awaitable[None]]]] = (
            {}
        )
        self.group_name = config.service_name
        self._running = False

    def register_event_handler(
        self, topic: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None:
        if topic not in self.event_handlers:
            self.event_handlers[topic] = []
        self.event_handlers[topic].append(handler)
        print(f"✅ [Redis] Registered event handler for stream '{topic}'")

    def register_command_handler(
        self, topic: str, handler: Callable[[Command], Awaitable[None]]
    ) -> None:
        if topic not in self.command_handlers:
            self.command_handlers[topic] = []
        self.command_handlers[topic].append(handler)
        print(f"✅ [Redis] Registered command handler for stream '{topic}'")

    async def start(self) -> None:
        """Start the Redis consumer loop."""
        # Verify connection first
        try:
            await self.redis_client.ping()
            print(f"✅ [Redis] Connected successfully to {self.config.redis_url}")
        except Exception as e:
            print(f"❌ [Redis] Connection failed to {self.config.redis_url}: {e}")
            return

        self._running = True
        print(
            f"🚀 [Redis] Parallel Stream Consumer starting on {self.config.redis_url}..."
        )
        tasks = []
        group_name = self.config.service_name
        consumer_name = f"{group_name}_{socket.gethostname()}"
        if self.event_handlers:
            tasks.append(
                self._listen_for_type(
                    MessageType.EVENT,
                    list(self.event_handlers.keys()),
                    group_name,
                    consumer_name,
                )
            )
        if self.command_handlers:
            tasks.append(
                self._listen_for_type(
                    MessageType.COMMAND,
                    list(self.command_handlers.keys()),
                    group_name,
                    consumer_name,
                )
            )
        tasks.append(self._process_scheduled_messages())
        if not tasks:
            print("⚠️ [Redis] No handlers registered. Consumer exiting.")
            return
        await asyncio.gather(*tasks)

    async def stop(self) -> None:
        self._running = False
        await self.redis_client.close()
        print("🛑 [Redis] Consumer stopped.")

    async def acknowledge(self, message: BaseMessage) -> None:
        broker_id = message.metadata.get("broker_id")
        topic = message.topic
        if broker_id and topic:
            try:
                await self.redis_client.xack(topic, self.group_name, broker_id)
            except Exception as e:
                print(
                    f"⚠️ [Redis] Failed to acknowledge message {broker_id} on {topic}: {e}"
                )

    async def _setup_stream(self, topic: str, group_name: str):
        try:
            await self.redis_client.xgroup_create(
                topic, group_name, id="0", mkstream=True
            )
            print(
                f"📦 [Redis] Created consumer group '{group_name}' for stream '{topic}'"
            )
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                print(f"❌ [Redis] Error creating group for '{topic}': {e}")
                raise e

    async def _listen_for_type(
        self,
        message_type: MessageType,
        topics: List[str],
        group_name: str,
        consumer_name: str,
    ) -> None:
        for topic in topics:
            await self._setup_stream(topic, group_name)
        asyncio.create_task(self._periodic_claim(topics, group_name, consumer_name))
        print(f"📥 [Redis] Listening to {message_type.value}: {topics}")
        processing_pending = True
        while self._running:
            try:
                current_id = "0" if processing_pending else ">"
                streams = {topic: current_id for topic in topics}
                results = await self.redis_client.xreadgroup(
                    group_name, consumer_name, streams, count=10, block=2000
                )
                total_messages = sum(len(msgs) for _, msgs in results) if results else 0
                if total_messages == 0:
                    if processing_pending:
                        processing_pending = False
                    continue
                for stream_name, messages in results:
                    for message_id, data in messages:
                        payload_json = data["payload"]
                        if message_type == MessageType.EVENT:
                            await self._handle_event_task(message_id, payload_json)
                        else:
                            await self._handle_command_task(message_id, payload_json)
            except Exception as e:
                print(f"❌ [Redis] Error in {message_type.value} listener loop: {e}")
                await asyncio.sleep(1)

    async def _handle_event_task(self, message_id: str, payload_json: str) -> None:
        try:
            event_dict = json.loads(payload_json)
            event = Event(**event_dict)
            event.metadata["broker_id"] = message_id
            for handler in self.event_handlers.get(event.topic, []):
                await handler(event)
        except Exception as e:
            topic = event.topic if "event" in locals() else "unknown"
            print(f"❌ [Redis] Error processing event {message_id} from {topic}: {e}")

    async def _handle_command_task(self, message_id: str, payload_json: str) -> None:
        try:
            cmd_dict = json.loads(payload_json)
            command = Command(**cmd_dict)
            command.metadata["broker_id"] = message_id
            for handler in self.command_handlers.get(command.topic, []):
                await handler(command)
        except Exception as e:
            topic = command.topic if "command" in locals() else "unknown"
            print(f"❌ [Redis] Error processing command {message_id} from {topic}: {e}")

    async def _periodic_claim(
        self, topics: List[str], group_name: str, consumer_name: str
    ) -> None:
        while self._running:
            try:
                await asyncio.sleep(300)
                for topic in topics:
                    await self._claim_stale_messages(topic, group_name, consumer_name)
            except Exception as e:
                print(f"❌ [Redis] Error in periodic claim task: {e}")

    async def _claim_stale_messages(
        self, topic: str, group_name: str, consumer_name: str
    ) -> None:
        min_idle_time = 600000
        try:
            pending = await self.redis_client.xpending_range(
                topic, group_name, "-", "+", 50, idle=min_idle_time
            )
            if not pending:
                return
            message_ids = [p["message_id"] for p in pending]
            if not message_ids:
                return
            claimed = await self.redis_client.xclaim(
                topic, group_name, consumer_name, min_idle_time, message_ids
            )
            if claimed:
                print(
                    f"🛠️ [Redis] Reclaimed {len(claimed)} stale messages on stream '{topic}'"
                )
        except Exception as e:
            print(f"❌ [Redis] Error claiming stale messages for {topic}: {e}")

    async def _process_scheduled_messages(self) -> None:
        queues = list(self.command_handlers.keys()) + list(self.event_handlers.keys())
        if not queues:
            return
        print(f"🕒 [Redis] Monitoring scheduled messages for streams: {queues}")
        while self._running:
            try:
                now = time.time()
                for topic in queues:
                    scheduled_key = f"scheduled:{topic}"
                    due_items = await self.redis_client.zrange(
                        scheduled_key, 0, now, byscore=True
                    )
                    if due_items:
                        for message_json in due_items:
                            if await self.redis_client.zrem(
                                scheduled_key, message_json
                            ):
                                await self.redis_client.xadd(
                                    topic, {"payload": message_json}
                                )
                                print(
                                    f"🚀 [Redis] Scheduled message moved to stream '{topic}'"
                                )
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ [Redis] Error in scheduler: {e}")
                await asyncio.sleep(1)
