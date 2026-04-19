from abc import ABC, abstractmethod
from typing import List


class BaseMessagingConfig(ABC):
    """
    Interface for messaging configuration required by the BaseMessagingHandler.
    Implemented by each service's Config class.
    """

    @property
    @abstractmethod
    def service_name(self) -> str:
        """The unique name of the service (e.g., 'data_collector_service')."""
        pass

    @property
    @abstractmethod
    def event_topics(self) -> List[str]:
        """The list of event topics this service should subscribe to."""
        pass
