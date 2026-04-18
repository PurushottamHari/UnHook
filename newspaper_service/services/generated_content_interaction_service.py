"""
Service for handling generated content interaction business logic.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..external.user_service import UserServiceClient
from ..models.generated_content_interaction import (
    GeneratedContentInteraction, InteractionStatus, InteractionType)
from ..models.generated_content_interaction_list import (
    GeneratedContentInteractionListData,
    GeneratedContentInteractionListResponse)
from ..repositories.generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from ..repositories.generated_content_repository import \
    GeneratedContentRepository
from .validations.validate_create_article_interaction_request_service import \
    ValidateCreateArticleInteractionRequestService


class ContentInteractionService:
    """Service for handling content interaction business logic."""

    def __init__(
        self,
        interaction_repository: GeneratedContentInteractionRepository,
        validation_service: ValidateCreateArticleInteractionRequestService,
        user_service_client: UserServiceClient,
        generated_content_repository: GeneratedContentRepository,
    ):
        """
        Initialize the service.

        Args:
            interaction_repository: Repository for interaction operations
            validation_service: Validation service for request validation
            user_service_client: Client for user service operations
            generated_content_repository: Repository for generated content operations
        """
        self._interaction_repository = interaction_repository
        self._validation_service = validation_service
        self._user_service_client = user_service_client
        self._generated_content_repository = generated_content_repository
        self.logger = logging.getLogger(__name__)

    async def create_interaction(
        self,
        generated_content_id: str,
        user_id: str,
        interaction_type: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> GeneratedContentInteraction:
        """
        Create an interaction with business logic validation.

        Args:
            generated_content_id: MongoDB _id of the generated content
            user_id: ID of the user
            interaction_type: Type of interaction (string, will be validated)
            metadata: Optional metadata (e.g., report reason)

        Returns:
            The created interaction

        Raises:
            ValueError: If user not found, content not found, interaction_type is invalid, or business rules are violated
        """
        # Validate and convert interaction_type string to enum
        try:
            interaction_type_enum = InteractionType(interaction_type.upper())
        except ValueError:
            raise ValueError(
                f"Invalid interaction_type: {interaction_type}. "
                f"Must be one of: LIKE, DISLIKE, REPORT, SAVED"
            )

        # Validate user exists
        user = self._user_service_client.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Validate content exists
        content = self._generated_content_repository.get_content_by_id(
            generated_content_id
        )
        if not content:
            raise ValueError(f"Content not found: {generated_content_id}")

        # Validate request
        validated_interaction_type, existing_interaction = (
            await self._validation_service.validate(
                generated_content_id, user_id, interaction_type_enum, metadata
            )
        )

        # If validation returned an existing interaction, update it
        if existing_interaction:
            # If same type is passed, handle based on interaction type
            if existing_interaction.interaction_type == validated_interaction_type:
                # For REPORT, raise error if already reported
                if validated_interaction_type == InteractionType.REPORT:
                    raise ValueError("Content already reported")

                # For LIKE, DISLIKE, and SAVED, toggle between ACTIVE and INACTIVE
                new_status = (
                    InteractionStatus.INACTIVE
                    if existing_interaction.status == InteractionStatus.ACTIVE
                    else InteractionStatus.ACTIVE
                )

                reason_map = {
                    InteractionType.LIKE: f"Like {'deactivated' if new_status == InteractionStatus.INACTIVE else 'activated'}",
                    InteractionType.DISLIKE: f"Dislike {'deactivated' if new_status == InteractionStatus.INACTIVE else 'activated'}",
                    InteractionType.SAVED: f"Save {'deactivated' if new_status == InteractionStatus.INACTIVE else 'activated'}",
                }

                existing_interaction.set_status(
                    new_status, reason=reason_map[validated_interaction_type]
                )

                return (
                    self._interaction_repository.update_generated_content_interaction(
                        existing_interaction
                    )
                )

            # For LIKE/DISLIKE, convert opposite type
            # Since we already checked same type above, existing must be opposite type
            if validated_interaction_type in (
                InteractionType.LIKE,
                InteractionType.DISLIKE,
            ):
                # Capture the old interaction type before changing it
                old_interaction_type = existing_interaction.interaction_type
                existing_interaction.set_interaction_type(validated_interaction_type)
                existing_interaction.metadata = metadata

                # Use override_interaction_type to filter by the old type while updating to new type
                return (
                    self._interaction_repository.update_generated_content_interaction(
                        existing_interaction,
                        override_interaction_type=old_interaction_type,
                    )
                )

            # For REPORT/SAVED, update metadata
            elif validated_interaction_type in (
                InteractionType.REPORT,
                InteractionType.SAVED,
            ):
                existing_interaction.metadata = metadata
                existing_interaction.updated_at = datetime.utcnow()
                return (
                    self._interaction_repository.update_generated_content_interaction(
                        existing_interaction
                    )
                )
            else:
                raise ValueError(
                    f"Unexpected interaction type: {validated_interaction_type.value}. "
                    f"Expected LIKE, DISLIKE, REPORT, or SAVED."
                )

        # Create new interaction
        interaction = GeneratedContentInteraction(
            id=uuid4(),
            generated_content_id=generated_content_id,
            user_id=user_id,
            interaction_type=validated_interaction_type,
            metadata=metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            status=InteractionStatus.ACTIVE,
        )
        return self._interaction_repository.create_generated_content_interaction(
            interaction
        )

    async def get_user_interaction(
        self,
        generated_content_id: str,
        user_id: str,
        interaction_type: InteractionType,
    ) -> Optional[GeneratedContentInteraction]:
        """
        Get a specific user interaction for content by type.

        Args:
            generated_content_id: MongoDB _id of the generated content
            user_id: ID of the user
            interaction_type: Type of interaction to retrieve

        Returns:
            The interaction if found, None otherwise

        Raises:
            ValueError: If user not found, content not found, or interaction_type is invalid
        """
        # Validate user exists
        user = self._user_service_client.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Validate content exists
        content = self._generated_content_repository.get_content_by_id(
            generated_content_id
        )
        if not content:
            raise ValueError(f"Content not found: {generated_content_id}")

        if not isinstance(interaction_type, InteractionType):
            try:
                interaction_type = InteractionType(interaction_type)
            except ValueError:
                raise ValueError(f"Invalid interaction_type: {interaction_type}")

        return self._interaction_repository.get_user_interaction(
            generated_content_id, user_id, interaction_type
        )

    async def list_user_interactions_for_content(
        self,
        generated_content_id: str,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> GeneratedContentInteractionListResponse:
        """
        List interactions for specific content with pagination.

        Args:
            generated_content_id: MongoDB _id of the generated content
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return (default=10, max=10)

        Returns:
            Paginated list response with interactions and hasNext flag

        Raises:
            ValueError: If content not found or page_limit exceeds maximum
        """
        # Validate page_limit
        if page_limit <= 0:
            raise ValueError("page_limit must be greater than 0")
        if page_limit > 10:
            raise ValueError("page_limit cannot exceed 10")

        # Validate content exists
        content = self._generated_content_repository.get_content_by_id(
            generated_content_id
        )
        if not content:
            raise ValueError(f"Content not found: {generated_content_id}")

        interactions, has_next = (
            self._interaction_repository.list_user_interactions_for_content(
                generated_content_id=generated_content_id,
                starting_after=starting_after,
                page_limit=page_limit,
            )
        )

        return GeneratedContentInteractionListResponse(
            data=GeneratedContentInteractionListData(
                list_response=interactions,
                hasNext=has_next,
            )
        )

    async def list_user_interactions(
        self,
        user_id: str,
        interaction_type: Optional[str] = None,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> GeneratedContentInteractionListResponse:
        """
        List user's interactions with pagination, optionally filtered by type.

        Args:
            user_id: ID of the user
            interaction_type: Optional filter by interaction type (string, will be validated)
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return (default=10, max=10)

        Returns:
            Paginated list response with interactions and hasNext flag

        Raises:
            ValueError: If user not found, interaction_type is invalid, or page_limit exceeds maximum
        """
        # Validate page_limit
        if page_limit <= 0:
            raise ValueError("page_limit must be greater than 0")
        if page_limit > 10:
            raise ValueError("page_limit cannot exceed 10")

        # Validate user exists
        user = self._user_service_client.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Validate and convert interaction_type string to enum if provided
        interaction_type_enum = None
        if interaction_type:
            try:
                interaction_type_enum = InteractionType(interaction_type.upper())
            except ValueError:
                raise ValueError(
                    f"Invalid interaction_type: {interaction_type}. "
                    f"Must be one of: LIKE, DISLIKE, REPORT, SAVED"
                )

        interactions, has_next = self._interaction_repository.list_user_interactions(
            user_id=user_id,
            interaction_type=interaction_type_enum,
            starting_after=starting_after,
            page_limit=page_limit,
        )

        return GeneratedContentInteractionListResponse(
            data=GeneratedContentInteractionListData(
                list_response=interactions,
                hasNext=has_next,
            )
        )
