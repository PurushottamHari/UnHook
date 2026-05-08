import time
from datetime import datetime

from injector import inject
from redis import asyncio as aioredis

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseMessage, Command, Event, MessageProducer
from newspaper_service.config.config import Config


@injectable()
class RedisMessageProducer(MessageProducer):
    @inject
    def __init__(self, config: Config):
        self.redis_client = aioredis.from_url(config.redis_url, decode_responses=True)

    async def publish_event(self, event: Event) -> None:
        message_json = event.model_dump_json()
        await self.redis_client.xadd(event.topic, {"payload": message_json})
        print(
            f"📡 [Redis] Event published to stream '{event.topic}': {event.event_type}"
        )

    async def publish_events(self, events: list[Event]) -> None:
        if not events:
            return
        async with self.redis_client.pipeline() as pipe:
            for event in events:
                message_json = event.model_dump_json()
                pipe.xadd(event.topic, {"payload": message_json})
            await pipe.execute()
        print(f"📡 [Redis] {len(events)} events batch published.")

    async def send_command(self, command: Command) -> None:
        message_json = command.model_dump_json()
        await self.redis_client.xadd(command.topic, {"payload": message_json})
        print(
            f"📤 [Redis] Command sent to stream '{command.topic}': {command.action_name}"
        )

    async def send_commands(self, commands: list[Command]) -> None:
        if not commands:
            return
        async with self.redis_client.pipeline() as pipe:
            for command in commands:
                message_json = command.model_dump_json()
                pipe.xadd(command.topic, {"payload": message_json})
            await pipe.execute()
        print(f"📤 [Redis] {len(commands)} commands batch sent.")

    async def schedule_command(self, command: Command, schedule_at: datetime) -> None:
        message_json = command.model_dump_json()
        timestamp = schedule_at.timestamp()
        scheduled_key = f"scheduled:{command.topic}"
        await self.redis_client.zadd(scheduled_key, {message_json: timestamp})
        print(
            f"⏰ [Redis] Command '{command.action_name}' scheduled for {schedule_at} on topic '{command.topic}'"
        )

    async def schedule_message(self, message: BaseMessage, delay_ms: int) -> None:
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
        dlq_stream = f"{service_name}:dead_letter_queue"
        original_topic = message.topic
        message.topic = dlq_stream
        message_json = message.model_dump_json()
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
        await self.redis_client.close()
