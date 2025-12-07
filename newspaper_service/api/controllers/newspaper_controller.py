"""
Controller handling HTTP requests for newspaper operations.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ...models.generated_content_list import GeneratedContentListResponse
from ...models.newspaper import Newspaper
from ...models.newspaper_list import NewspaperListResponse
from ...models.newspaper_response import NewspaperResponse
from ...services.generated_content_service import GeneratedContentService
from ...services.newspaper_service import NewspaperService
from ..dependencies import (get_generated_content_service,
                            get_newspaper_service, get_user_id_from_header)

router = APIRouter(tags=["newspapers"])


@router.get(
    "/newspapers/{newspaper_id}",
    response_model=NewspaperResponse,
)
async def get_newspaper_by_id(
    newspaper_id: str,
    user_id: str = Depends(get_user_id_from_header),
    newspaper_service: NewspaperService = Depends(get_newspaper_service),
) -> NewspaperResponse:
    """
    Get a newspaper by its ID, validating it belongs to the user.

    Args:
        newspaper_id: ID of the newspaper
        user_id: User ID from X-User-ID header
        newspaper_service: Injected newspaper service

    Returns:
        NewspaperResponse: The newspaper object with Unix timestamps

    Raises:
        HTTPException: If newspaper not found or doesn't belong to user
    """
    try:
        newspaper = await newspaper_service.get_newspaper_by_id(
            newspaper_id=newspaper_id, user_id=user_id
        )
        return NewspaperResponse.from_newspaper(newspaper)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/newspapers",
    response_model=NewspaperListResponse,
)
async def list_newspapers(
    user_id: str = Depends(get_user_id_from_header),
    date: Optional[str] = Query(
        None, description="Optional date filter in DD/MM/YYYY format"
    ),
    starting_after: Optional[str] = Query(
        None, description="Cursor ID to start after (for pagination)"
    ),
    page_limit: int = Query(
        10, le=10, description="Maximum number of items to return (max 10)"
    ),
    newspaper_service: NewspaperService = Depends(get_newspaper_service),
) -> NewspaperListResponse:
    """
    List newspapers for a user with pagination, optionally filtered by date.

    Args:
        user_id: User ID from X-User-ID header
        date: Optional date filter in DD/MM/YYYY format
        starting_after: Optional cursor ID to start after (for pagination)
        page_limit: Maximum number of items to return (default=10, max=10)
        newspaper_service: Injected newspaper service

    Returns:
        Paginated list response with newspapers and hasNext flag

    Raises:
        HTTPException: If retrieval fails or invalid parameters
    """
    try:
        return await newspaper_service.list_newspapers(
            user_id=user_id,
            date=date,
            starting_after=starting_after,
            page_limit=page_limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/newspapers/{newspaper_id}/generated_content",
    response_model=GeneratedContentListResponse,
)
async def list_generated_content_for_newspaper(
    newspaper_id: str,
    user_id: str = Depends(get_user_id_from_header),
    starting_after: Optional[str] = Query(
        None, description="Cursor ID to start after (for pagination)"
    ),
    page_limit: int = Query(
        10, le=10, description="Maximum number of items to return (max 10)"
    ),
    content_service: GeneratedContentService = Depends(get_generated_content_service),
) -> GeneratedContentListResponse:
    """
    List generated content for a specific newspaper with pagination, including active user interactions.

    Args:
        newspaper_id: ID of the newspaper
        user_id: User ID from X-User-ID header
        starting_after: Optional cursor ID to start after (for pagination)
        page_limit: Maximum number of items to return (default=10, max=10)
        content_service: Injected content service

    Returns:
        Paginated list response with content, active interactions, and hasNext flag

    Raises:
        HTTPException: If newspaper not found, user not found, or retrieval fails
    """
    try:
        return await content_service.list_generated_content_for_newspaper(
            newspaper_id=newspaper_id,
            user_id=user_id,
            starting_after=starting_after,
            page_limit=page_limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
