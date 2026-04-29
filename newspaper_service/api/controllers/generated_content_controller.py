"""
Controller handling HTTP requests for generated content interaction operations.
"""

from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_class import View
from pydantic import BaseModel

from ...models.generated_content_interaction import GeneratedContentInteraction
from ...models.generated_content_interaction_list import \
    GeneratedContentInteractionListResponse
from ...models.generated_content_response import GeneratedContentResponse
from ...services.generated_content_interaction_service import \
    ContentInteractionService
from ...services.generated_content_service import GeneratedContentService
from ..dependencies import Injected, get_user_id_from_header

router = APIRouter(tags=["content-interactions"])


class InteractionRequest(BaseModel):
    """Request model for creating/updating an interaction."""

    user_id: str
    interaction_type: str
    metadata: Optional[Dict[str, str]] = None


@View(router)
class GeneratedContentController:
    interaction_service: ContentInteractionService = Injected(ContentInteractionService)
    content_service: GeneratedContentService = Injected(GeneratedContentService)

    @router.post(
        "/generated_content/{generated_content_id}/user_interaction",
        response_model=GeneratedContentInteraction,
    )
    async def create_interaction(
        self,
        generated_content_id: str,
        request: InteractionRequest,
    ) -> GeneratedContentInteraction:
        """
        Create a user interaction for generated content.
        """
        try:
            return await self.interaction_service.create_interaction(
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
        self,
        content_id: str,
        starting_after: Optional[str] = Query(
            None, description="Cursor ID to start after (for pagination)"
        ),
        page_limit: int = Query(
            10, le=10, description="Maximum number of items to return (max 10)"
        ),
    ) -> GeneratedContentInteractionListResponse:
        """
        List interactions for specific content with pagination.
        """
        try:
            return await self.interaction_service.list_user_interactions_for_content(
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
        self,
        interaction_type: Optional[str] = Query(
            None,
            description="Filter by interaction type (LIKE, DISLIKE, REPORT, SAVED)",
        ),
        starting_after: Optional[str] = Query(
            None, description="Cursor ID to start after (for pagination)"
        ),
        page_limit: int = Query(
            10, le=10, description="Maximum number of items to return (max 10)"
        ),
        user_id: str = Depends(get_user_id_from_header),
    ) -> GeneratedContentInteractionListResponse:
        """
        List user's interactions with pagination, optionally filtered by type.
        """
        try:
            return await self.interaction_service.list_user_interactions(
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
        self,
        content_id: str,
    ) -> GeneratedContentResponse:
        """
        Get generated content by its ID.
        """
        try:
            content, user_collected_content = (
                await self.content_service.get_generated_content_by_id(
                    content_id=content_id
                )
            )
            return GeneratedContentResponse.from_generated_content(
                content, user_collected_content
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
