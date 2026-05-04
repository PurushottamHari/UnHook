import asyncio

from commons.messaging import BaseMessagingHandler
from data_collector_service.infra.dependency_injection.registration import \
    create_injector


async def main():
    # Initialize the DI container
    injector = create_injector()

    # Get the BaseMessagingHandler from the injector
    messaging_handler = injector.get(BaseMessagingHandler)

    try:
        # Start the messaging orchestrator
        await messaging_handler.start()
    except KeyboardInterrupt:
        await messaging_handler.stop()


if __name__ == "__main__":
    asyncio.run(main())
