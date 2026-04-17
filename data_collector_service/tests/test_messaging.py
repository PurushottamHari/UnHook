import asyncio
from unittest.mock import MagicMock, AsyncMock

from commons.messaging import Command, Event
from data_collector_service.messaging.redis.producer import RedisMessageProducer
from data_collector_service.messaging.redis.consumer import RedisMessageConsumer
from data_collector_service.messaging.handlers import register_handlers
from data_collector_service.services.collection.collection_service import (
    CollectionService,
)
from data_collector_service.services.rejection.reject_content_service import (
    RejectContentService,
)


async def run_messaging_test():
    """
    Test the full messaging flow from producer to consumer.
    Note: Requires a running Redis on localhost:6379.
    """
    host = "localhost"
    port = 6379
    db = 0

    # 1. Setup mocks for services
    mock_collector = MagicMock(spec=CollectionService)
    mock_rejection = MagicMock(spec=RejectContentService)
    mock_rejection.reject = AsyncMock()

    # 2. Setup producer and consumer
    producer = RedisMessageProducer(host=host, port=port, db=db)
    consumer = RedisMessageConsumer(host=host, port=port, db=db)

    # 3. Register handlers
    register_handlers(consumer, mock_collector, mock_rejection)

    # 4. Start consumer in background
    consumer_task = asyncio.create_task(consumer.start())
    await asyncio.sleep(0.5)  # Give it time to start/subscribe

    try:
        # Unified command topic used by the service
        command_topic = "data_collector.commands"
        user_id = "test-user-123"

        # 5. Send a collect_data command
        command = Command(
            target_service="data-collector-service",
            action_name="collect_data",
            payload={"user_id": user_id},
        )
        print(f"🚀 [Test] Sending 'collect_data' to {command_topic}")
        await producer.send_command(command_topic, command)

        # 6. Wait for processing
        await asyncio.sleep(1.0)

        # 7. Verify collector was called
        mock_collector.collect_for_user.assert_called_once_with(user_id)
        print("✅ [Test] collect_data command handled correctly")

        # 8. Send a reject_content command
        reject_command = Command(
            target_service="data_collector_service",
            action_name="reject_content",
            payload={"user_id": user_id},
        )
        print(f"🚀 [Test] Sending 'reject_content' to {command_topic}")
        await producer.send_command(command_topic, reject_command)

        # 9. Wait for processing
        await asyncio.sleep(1.0)

        # 10. Verify rejection was called
        mock_rejection.reject.assert_called_once_with(user_id)
        print("✅ [Test] reject_content command handled correctly")

    finally:
        # Cleanup
        await consumer.stop()
        await producer.close()
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    print("🧪 Running Messaging Integration Test...")
    asyncio.run(run_messaging_test())
