import asyncio
from data_collector_service.infra.dependency_injection.registration import (
    create_injector,
)
from data_collector_service.messaging.messaging_handler import MessagingHandler


async def main():
    # Initialize the DI container
    injector = create_injector()

    # Get the MessagingHandler from the injector
    messaging_handler = injector.get(MessagingHandler)

    try:
        # Start the messaging orchestrator
        await messaging_handler.start()
    except KeyboardInterrupt:
        await messaging_handler.stop()


if __name__ == "__main__":
    asyncio.run(main())
