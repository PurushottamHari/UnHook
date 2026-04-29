"""
Dependency injection setup for the API.
"""

from fastapi import Depends, Header, HTTPException, Request
from injector import Injector, T
from typing_extensions import Annotated


def get_injector(request: Request) -> Injector:
    """Get the DI injector from the app state."""
    return request.app.state.injector


def Injected(cls: type[T]) -> T:
    """
    A generic helper to resolve classes from the global injector.
    Usage: service: MyService = Injected(MyService)
    """
    return Depends(lambda request: request.app.state.injector.get(cls))


async def get_user_id_from_header(
    user_id: Annotated[
        str, Header(alias="X-User-ID", description="User ID from header")
    ],
) -> str:
    """
    Extract user_id from X-User-ID header.
    """
    if not user_id:
        raise HTTPException(
            status_code=401, detail="User ID header (X-User-ID) is required"
        )
    return user_id
