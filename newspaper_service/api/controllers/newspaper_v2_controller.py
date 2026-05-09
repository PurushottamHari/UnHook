from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ...services.newspaper_api_service import NewspaperApiService
from ..dependencies import get_user_id_from_header
from ..models.newspaper_v2_response import NewspaperV2Response

router = APIRouter(tags=["newspapers_v2"])


class NewspaperV2Controller:
    """Controller for consolidated Newspaper V2 operations."""

    def __init__(self, request: Request):
        # Resolve services once from the injector in the constructor
        injector = request.app.state.injector
        self.newspaper_api_service = injector.get(NewspaperApiService)

    async def get_newspaper_with_articles_v2(
        self,
        date: str,
        starting_after: Optional[str],
        user_id: str,
        timezone: str = "UTC",
    ) -> NewspaperV2Response:
        """Core logic for getting newspaper with articles."""
        try:
            return await self.newspaper_api_service.get_newspaper_with_articles_v2(
                user_id=user_id,
                date_str=date,
                starting_after=starting_after,
                timezone_str=timezone,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# Native FastAPI route registration
@router.get(
    "/v2/newspapers/by-date",
    response_model=NewspaperV2Response,
)
async def get_newspaper_with_articles_v2_endpoint(
    date: str = Query(..., description="Date in DD/MM/YYYY format"),
    starting_after: Optional[str] = Query(
        None, description="External ID cursor for pagination"
    ),
    timezone: str = Query(
        "UTC", description="Timezone for the request (e.g. Asia/Kolkata)"
    ),
    user_id: str = Depends(get_user_id_from_header),
    controller: NewspaperV2Controller = Depends(),
) -> NewspaperV2Response:
    return await controller.get_newspaper_with_articles_v2(
        date=date, starting_after=starting_after, user_id=user_id, timezone=timezone
    )
