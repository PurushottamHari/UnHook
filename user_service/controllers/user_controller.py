"""
User controller handling HTTP requests for user operations.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ..api.dependencies import get_user_service
from ..models.user import User
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User)
async def create_user(
    user_data: Dict[str, Any], user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Create a new user.

    Args:
        user_data: Dictionary containing user data
        user_service: Injected user service

    Returns:
        Created user object

    Raises:
        HTTPException: If user creation fails
    """
    try:
        user = User(**user_data)
        return await user_service.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str, user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Get a user by their ID.

    Args:
        user_id: UUID of the user to retrieve
        user_service: Injected user service

    Returns:
        User object if found

    Raises:
        HTTPException: If user not found
    """
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
