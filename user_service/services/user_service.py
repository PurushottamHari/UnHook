"""
User service implementing business logic for user operations.
"""

from typing import Optional
from uuid import UUID
from ..models.user import User
from ..repositories.user_repository import UserRepository

class UserService:
    """Service for handling user-related business logic."""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def create_user(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User object to create
            
        Returns:
            Created user object
        """
        return await self._user_repository.create_user(user)
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: UUID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return await self._user_repository.get_user(user_id) 