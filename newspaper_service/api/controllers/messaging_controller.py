"""
Controller for internal messaging operations.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from ...services.messaging import (ProcessNewspaperForUserMessagingService,
                                   StartUserCollectionMessagingService)

router = APIRouter(prefix="/internal", tags=["internal"])


class MessagingController:
    """Controller for triggering internal messaging events."""

    def __init__(self, request: Request):
        # Resolve services once from the injector in the constructor
        injector = request.app.state.injector
        self.start_user_collection_service = injector.get(
            StartUserCollectionMessagingService
        )
        self.process_newspaper_service = injector.get(
            ProcessNewspaperForUserMessagingService
        )
        self.logger = logging.getLogger(__name__)

    async def start_user_collection(self, user_id: str):
        """
        Manually trigger user collection for a specific user.
        """
        try:
            await self.start_user_collection_service.execute(user_id=user_id)
            return {
                "status": "success",
                "message": f"User collection triggered for {user_id}",
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error triggering user collection: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def process_newspaper_for_user(self, user_id: str):
        """
        Manually trigger newspaper creation for a specific user.
        """
        try:
            await self.process_newspaper_service.execute(user_id=user_id)
            return {
                "status": "success",
                "message": f"Newspaper creation triggered for {user_id}",
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error triggering newspaper creation: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


# Native FastAPI route registration
@router.post("/start_user_collection/{user_id}")
async def start_user_collection_endpoint(
    user_id: str,
    controller: MessagingController = Depends(),
):
    return await controller.start_user_collection(user_id=user_id)


@router.post("/process_newspaper_for_user/{user_id}")
async def process_newspaper_for_user_endpoint(
    user_id: str,
    controller: MessagingController = Depends(),
):
    return await controller.process_newspaper_for_user(user_id=user_id)
