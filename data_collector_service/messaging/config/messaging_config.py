from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseMessagingConfig
from data_collector_service.config.config import Config


@injectable()
class MessagingConfig(BaseMessagingConfig):
    """
    Implementation of BaseMessagingConfig for data_collector_service.
    Delegates to the main service Config.
    """

    @inject
    def __init__(self, config: Config):
        self._config = config

    @property
    def service_name(self) -> str:
        return self._config.service_name

    @property
    def event_topics(self) -> List[str]:
        # You can also hardcode these here if they are purely messaging-level
        return self._config.get("messaging.event_topics", [])
