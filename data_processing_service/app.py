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


async def main():
    logger.info("🚀 Starting Data Processing Service...")

    # Initialize the DI container
    injector = create_injector()

    # Get the BaseMessagingHandler from the injector
    messaging_handler = injector.get(BaseMessagingHandler)

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
