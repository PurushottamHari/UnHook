from abc import ABC, abstractmethod
from user_service.models.user import User

class BaseStaticCollector(ABC):
    """Base class for static data collection."""
    
    @abstractmethod
    def collect(self, user: User) -> None:
        """
        Collect static data for the given user.
        
        Args:
            user: User object containing user configuration and preferences
        """
        pass 