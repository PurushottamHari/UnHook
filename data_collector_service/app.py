import asyncio
import os

from commons.messaging import BaseMessagingHandler
from data_collector_service.infra.dependency_injection.registration import \
    create_injector
from data_collector_service.messaging.models.commands import (
    EnrichYouTubeVideoForUserCommand, EnrichYouTubeVideoForUserPayload)
from data_collector_service.messaging.routers.command_router import \
    CommandRouter


async def main():
    # Initialize the DI container
    injector = create_injector()

    # Get the BaseMessagingHandler from the injector
    messaging_handler = injector.get(BaseMessagingHandler)
    # await debug_command(injector)

    try:
        # Start the messaging orchestrator
        await messaging_handler.start()
    except KeyboardInterrupt:
        await messaging_handler.stop()


async def debug_command(injector):

    # Get the CommandRouter from the injector
    command_router = injector.get(CommandRouter)

    # Construct the exact command from the DLQ message
    payload = EnrichYouTubeVideoForUserPayload(
        user_id="607d95f0-47ef-444c-89d2-d05f257d1265",
        video_id="60Cf_y6Jmw4",
        user_collected_content_id="75a29d18-bf42-4a7a-8fce-b75998c49b3f",
        channel_name="sadhguru",
    )

    command = EnrichYouTubeVideoForUserCommand(payload=payload)
    try:
        await command_router.handle_domain_command(command)
        print("✅ [Debug] Command executed successfully")
    except Exception as e:
        print(f"❌ [Debug] Command failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
