from abc import ABC, abstractmethod
from user_service.models.user import User

class BaseDiscoverCollector(ABC):
    """Base class for discover data collection."""
    
    @abstractmethod
    def collect(self, user: User) -> None:
        """
        Collect discover data for the given user.
        
        Args:
            user: User object containing user configuration and preferences
        """
        pass 