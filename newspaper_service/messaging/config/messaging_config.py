from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseMessagingConfig, Event
from commons.messaging.contracts.events.data_collector_service.models import (
    UserCollectedContentReadyToBeUsedEvent,
    UserCollectedContentReadyToUsedPayload)
from newspaper_service.config.config import Config


@injectable()
class MessagingConfig(BaseMessagingConfig):
    @inject
    def __init__(self, config: Config):
        self._config = config

    @property
    def redis_host(self) -> str:
        return self._config.redis_host

    @property
    def redis_port(self) -> int:
        return self._config.redis_port

    @property
    def redis_db(self) -> int:
        return self._config.redis_db

    @property
    def service_name(self) -> str:
        return self._config.service_name

    @property
    def command_topic(self) -> str:
        return self._config.messaging_command_topic

    @property
    def event_topic(self) -> str:
        return self._config.messaging_event_topic

    @property
    def interested_events(self) -> List[Event]:
        """The list of events this service should subscribe to."""
        return [
            UserCollectedContentReadyToBeUsedEvent(
                payload=UserCollectedContentReadyToUsedPayload(
                    user_id="junk",
                    user_collected_content_id="junk",
                    external_id="junk",
                )
            )
        ]
