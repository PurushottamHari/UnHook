"""
Controller handling HTTP requests for newspaper operations.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ...models.generated_content_list import GeneratedContentListResponse
from ...models.newspaper import Newspaper
from ...models.newspaper_list import NewspaperListResponse
from ...models.newspaper_response import NewspaperResponse
from ...services.generated_content_service import GeneratedContentService
from ...services.newspaper_service import NewspaperService
from ..dependencies import get_user_id_from_header

router = APIRouter(tags=["newspapers"])


class NewspaperController:
    """Controller handling HTTP requests for newspaper operations."""

    def __init__(self, request: Request):
        # Resolve services once from the injector in the constructor
        injector = request.app.state.injector
        self.newspaper_service = injector.get(NewspaperService)
        self.content_service = injector.get(GeneratedContentService)

    async def get_newspaper_by_id(
        self,
        newspaper_id: str,
        user_id: str,
    ) -> NewspaperResponse:
        """
        Get a newspaper by its ID, validating it belongs to the user.
        """
        try:
            newspaper = await self.newspaper_service.get_newspaper_by_id(
                newspaper_id=newspaper_id, user_id=user_id
            )
            return NewspaperResponse.from_newspaper(newspaper)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_newspapers(
        self,
        user_id: str,
        date: Optional[str],
        starting_after: Optional[str],
        page_limit: int,
    ) -> NewspaperListResponse:
        """
        List newspapers for a user with pagination, optionally filtered by date.
        """
        try:
            return await self.newspaper_service.list_newspapers(
                user_id=user_id,
                date=date,
                starting_after=starting_after,
                page_limit=page_limit,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_generated_content_for_newspaper(
        self,
        newspaper_id: str,
        user_id: str,
        starting_after: Optional[str],
        page_limit: int,
    ) -> GeneratedContentListResponse:
        """
        List generated content for a specific newspaper with pagination.
        """
        try:
            return await self.content_service.list_generated_content_for_newspaper(
                newspaper_id=newspaper_id,
                user_id=user_id,
                starting_after=starting_after,
                page_limit=page_limit,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# Native FastAPI route registration
@router.get(
    "/newspapers/{newspaper_id}",
    response_model=NewspaperResponse,
)
async def get_newspaper_by_id_endpoint(
    newspaper_id: str,
    user_id: str = Depends(get_user_id_from_header),
    controller: NewspaperController = Depends(),
) -> NewspaperResponse:
    return await controller.get_newspaper_by_id(
        newspaper_id=newspaper_id, user_id=user_id
    )


@router.get(
    "/newspapers",
    response_model=NewspaperListResponse,
)
async def list_newspapers_endpoint(
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
    controller: NewspaperController = Depends(),
) -> NewspaperListResponse:
    return await controller.list_newspapers(
        user_id=user_id,
        date=date,
        starting_after=starting_after,
        page_limit=page_limit,
    )


@router.get(
    "/newspapers/{newspaper_id}/generated_content",
    response_model=GeneratedContentListResponse,
)
async def list_generated_content_for_newspaper_endpoint(
    newspaper_id: str,
    user_id: str = Depends(get_user_id_from_header),
    starting_after: Optional[str] = Query(
        None, description="Cursor ID to start after (for pagination)"
    ),
    page_limit: int = Query(
        10, le=10, description="Maximum number of items to return (max 10)"
    ),
    controller: NewspaperController = Depends(),
) -> GeneratedContentListResponse:
    return await controller.list_generated_content_for_newspaper(
        newspaper_id=newspaper_id,
        user_id=user_id,
        starting_after=starting_after,
        page_limit=page_limit,
    )
