"""
Dependency injection setup for the API.
"""

from fastapi import Depends
from ..repositories.mongodb import MongoDBUserRepository
from ..services.user_service import UserService

async def get_user_repository() -> MongoDBUserRepository:
    """Get MongoDB user repository instance."""
    return MongoDBUserRepository()

async def get_user_service(
    repository: MongoDBUserRepository = Depends(get_user_repository)
) -> UserService:
    """Get user service instance with repository dependency."""
    return UserService(repository) 