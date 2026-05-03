import asyncio
import logging

from commons.messaging import BaseMessagingHandler
from data_processing_service.infra.dependency_injection.registration import \
    create_injector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_local_commands(injector):
    from commons.messaging import BaseCommandRouter, Command

    command_router = injector.get(BaseCommandRouter)
    await command_router.handle_domain_command(
        Command(
            message_id="bd6b2267-3865-47e4-8694-f0c928d4165b",
            target_service="data_processing_service",
            action_name="generate_complete_youtube_content",
            payload={
                "generated_content_id": "5d6dd3e5-ca91-4868-a92f-75a399783464",
            },
            topic="data_processing_service:commands",
        )
    )
    return


async def main():
    logger.info("🚀 Starting Data Processing Service...")

    # Initialize the DI container
    injector = create_injector()

    # Get the BaseMessagingHandler from the injector
    messaging_handler = injector.get(BaseMessagingHandler)

    # Run local commands for debugging
    # await run_local_commands(injector)

    try:
        # Start the messaging orchestrator
        await messaging_handler.start()
    except KeyboardInterrupt:
        logger.info("Stopping Data Processing Service...")
        await messaging_handler.stop()
    except Exception as e:
        logger.error(f"Error in Data Processing Service: {e}", exc_info=True)
        await messaging_handler.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
