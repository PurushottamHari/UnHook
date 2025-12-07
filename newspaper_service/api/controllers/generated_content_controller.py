"""
Controller handling HTTP requests for generated content interaction operations.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from data_processing_service.models.generated_content import GeneratedContent

from ...models.generated_content_interaction import GeneratedContentInteraction
from ...models.generated_content_interaction_list import \
    GeneratedContentInteractionListResponse
from ...models.generated_content_response import GeneratedContentResponse
from ...services.generated_content_interaction_service import \
    ContentInteractionService
from ...services.generated_content_service import GeneratedContentService
from ..dependencies import (get_generated_content_interaction_service,
                            get_generated_content_service,
                            get_user_id_from_header)

router = APIRouter(tags=["content-interactions"])


class InteractionRequest(BaseModel):
    """Request model for creating/updating an interaction."""

    user_id: str
    interaction_type: str
    metadata: Optional[Dict[str, str]] = None


@router.post(
    "/generated_content/{generated_content_id}/user_interaction",
    response_model=GeneratedContentInteraction,
)
async def create_interaction(
    generated_content_id: str,
    request: InteractionRequest,
    interaction_service: ContentInteractionService = Depends(
        get_generated_content_interaction_service
    ),
) -> GeneratedContentInteraction:
    """
    Create a user interaction for generated content.

    Args:
        generated_content_id: MongoDB _id of the generated content
        request: Interaction request data
        interaction_service: Injected interaction service

    Returns:
        Created interaction object

    Raises:
        HTTPException: If interaction creation fails
    """
    try:
        return await interaction_service.create_interaction(
            generated_content_id=generated_content_id,
            user_id=request.user_id,
            interaction_type=request.interaction_type,
            metadata=request.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/list_user_interactions_for_content/{content_id}",
    response_model=GeneratedContentInteractionListResponse,
)
async def list_user_interactions_for_content(
    content_id: str,
    starting_after: Optional[str] = Query(
        None, description="Cursor ID to start after (for pagination)"
    ),
    page_limit: int = Query(
        10, le=10, description="Maximum number of items to return (max 10)"
    ),
    interaction_service: ContentInteractionService = Depends(
        get_generated_content_interaction_service
    ),
) -> GeneratedContentInteractionListResponse:
    """
    List interactions for specific content with pagination.

    Args:
        content_id: MongoDB _id of the generated content
        starting_after: Optional cursor ID to start after (for pagination)
        page_limit: Maximum number of items to return (default=10, max=10)
        interaction_service: Injected interaction service

    Returns:
        Paginated list response with interactions and hasNext flag
    """
    try:
        return await interaction_service.list_user_interactions_for_content(
            generated_content_id=content_id,
            starting_after=starting_after,
            page_limit=page_limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/list_user_interactions",
    response_model=GeneratedContentInteractionListResponse,
)
async def list_user_interactions(
    interaction_type: Optional[str] = Query(
        None, description="Filter by interaction type (LIKE, DISLIKE, REPORT, SAVED)"
    ),
    starting_after: Optional[str] = Query(
        None, description="Cursor ID to start after (for pagination)"
    ),
    page_limit: int = Query(
        10, le=10, description="Maximum number of items to return (max 10)"
    ),
    user_id: str = Depends(get_user_id_from_header),
    interaction_service: ContentInteractionService = Depends(
        get_generated_content_interaction_service
    ),
) -> GeneratedContentInteractionListResponse:
    """
    List user's interactions with pagination, optionally filtered by type.

    Args:
        interaction_type: Optional filter by interaction type
        starting_after: Optional cursor ID to start after (for pagination)
        page_limit: Maximum number of items to return (default=10, max=10)
        user_id: User ID from X-User-ID header
        interaction_service: Injected interaction service

    Returns:
        Paginated list response with interactions and hasNext flag
    """
    try:
        return await interaction_service.list_user_interactions(
            user_id=user_id,
            interaction_type=interaction_type,
            starting_after=starting_after,
            page_limit=page_limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/generated_content/{content_id}",
    response_model=GeneratedContentResponse,
)
async def get_generated_content(
    content_id: str,
    content_service: GeneratedContentService = Depends(get_generated_content_service),
) -> GeneratedContentResponse:
    """
    Get generated content by its ID.

    Args:
        content_id: MongoDB _id of the generated content
        content_service: Injected content service

    Returns:
        GeneratedContentResponse: The generated content object with Unix timestamps

    Raises:
        HTTPException: If content not found or retrieval fails
    """
    try:
        content = await content_service.get_generated_content_by_id(
            content_id=content_id
        )
        return GeneratedContentResponse.from_generated_content(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
