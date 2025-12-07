"""
Service for handling newspaper business logic.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from ..external.user_service import UserServiceClient
from ..models.newspaper import Newspaper
from ..models.newspaper_list import NewspaperListData, NewspaperListResponse
from ..repositories.newspaper_repository import NewspaperRepository


class NewspaperService:
    """Service for handling newspaper business logic."""

    def __init__(
        self,
        newspaper_repository: NewspaperRepository,
        user_service_client: UserServiceClient,
    ):
        """
        Initialize the service.

        Args:
            newspaper_repository: Repository for newspaper operations
            user_service_client: Client for user service operations
        """
        self._newspaper_repository = newspaper_repository
        self._user_service_client = user_service_client
        self.logger = logging.getLogger(__name__)

    async def get_newspaper_by_id(
        self, newspaper_id: str, user_id: str
    ) -> Newspaper:
        """
        Get a newspaper by its ID, validating it belongs to the user.

        Args:
            newspaper_id: ID of the newspaper
            user_id: User ID to validate ownership

        Returns:
            Newspaper: The newspaper object

        Raises:
            HTTPException: If user not found, newspaper not found, or doesn't belong to user
        """
        # Validate user exists
        user = self._user_service_client.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User not found: {user_id}"
            )

        newspaper = self._newspaper_repository.get_newspaper(newspaper_id)
        if not newspaper:
            raise HTTPException(
                status_code=404, detail=f"Newspaper not found: {newspaper_id}"
            )

        if newspaper.user_id != user_id:
            raise HTTPException(
                status_code=404, detail=f"Newspaper not found: {newspaper_id}"
            )

        return newspaper

    async def list_newspapers(
        self,
        user_id: str,
        date: Optional[str] = None,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> NewspaperListResponse:
        """
        List newspapers for a user with pagination, optionally filtered by date.

        Args:
            user_id: User ID to filter newspapers
            date: Optional date string in DD/MM/YYYY format
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return (default=10, max=10)

        Returns:
            Paginated list response with newspapers and hasNext flag

        Raises:
            HTTPException: If user not found
            ValueError: If page_limit exceeds maximum or date format is invalid
        """
        # Validate user exists
        user = self._user_service_client.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User not found: {user_id}"
            )

        # Validate page_limit
        if page_limit <= 0:
            raise ValueError("page_limit must be greater than 0")
        if page_limit > 10:
            raise ValueError("page_limit cannot exceed 10")

        # Parse date if provided
        for_date = None
        if date:
            try:
                for_date = datetime.strptime(date, "%d/%m/%Y")
                # Set timezone to UTC if not present
                if for_date.tzinfo is None:
                    from datetime import timezone

                    for_date = for_date.replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise ValueError(f"Invalid date format. Expected DD/MM/YYYY: {date}") from e

        # Request page_limit + 1 items to determine hasNext
        newspapers = self._newspaper_repository.list_newspapers_by_user(
            user_id=user_id,
            for_date=for_date,
            starting_after=starting_after,
            page_limit=page_limit + 1,
        )

        # Determine hasNext and take only page_limit items
        has_next = len(newspapers) > page_limit
        newspapers_to_return = newspapers[:page_limit]

        return NewspaperListResponse(
            data=NewspaperListData(
                list_response=newspapers_to_return,
                hasNext=has_next,
            )
        )

