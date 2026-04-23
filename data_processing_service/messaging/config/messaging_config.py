from typing import List

from injector import inject

from commons.messaging import BaseMessagingConfig
from data_processing_service.config.config import Config


class MessagingConfig(BaseMessagingConfig):
    @inject
    def __init__(self, config: Config):
        self._config = config

    @property
    def service_name(self) -> str:
        return self._config.service_name

    @property
    def event_topics(self) -> List[str]:
        # Return any topics this service should listen to
        # Example: return ["data_collector_service.events"]
        return []

    # Extra properties for internal use if needed
    @property
    def redis_host(self) -> str:
        return self._config.redis_host

    @property
    def redis_port(self) -> int:
        return self._config.redis_port

    @property
    def redis_db(self) -> int:
        return self._config.redis_db
