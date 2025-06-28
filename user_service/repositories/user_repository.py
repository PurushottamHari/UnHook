"""
User repository interface defining the contract for database operations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ..models.user import User

class UserRepository(ABC):
    """Interface for user data storage operations."""
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user in the database."""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user by their ID."""
        pass 