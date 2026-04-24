from abc import ABC, abstractmethod
from typing import List

from .models import Event


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
    def interested_events(self) -> List[Event]:
        """The list of events this service should subscribe to."""
        pass
