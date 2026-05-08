from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseMessagingConfig, Event
from commons.messaging.contracts.events.data_processing_service.models import (
    GeneratedYoutubeContentArticleReadyEvent,
    GeneratedYoutubeContentArticleReadyPayload)
from data_collector_service.config.config import Config


@injectable()
class MessagingConfig(BaseMessagingConfig):
    """
    Implementation of BaseMessagingConfig for data_collector_service.
    """

    @inject
    def __init__(self, config: Config):
        self._config = config

    @property
    def service_name(self) -> str:
        return self._config.service_name

    @property
    def interested_events(self) -> List[Event]:
        return [
            GeneratedYoutubeContentArticleReadyEvent(
                payload=GeneratedYoutubeContentArticleReadyPayload(
                    user_id="junk",
                    generated_content_id="junk",
                    external_id="junk",
                )
            )
        ]
