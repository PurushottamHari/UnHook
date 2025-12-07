"""
Service for validating create content interaction requests.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from ...models.generated_content_interaction import (
    GeneratedContentInteraction, InteractionType)
from ...repositories.generated_content_interaction_repository import \
    GeneratedContentInteractionRepository


class ValidateCreateArticleInteractionRequestService:
    """Service for validating create content interaction requests."""

    def __init__(
        self,
        interaction_repository: GeneratedContentInteractionRepository,
    ):
        """
        Initialize the validation service.

        Args:
            interaction_repository: Repository for interaction operations
        """
        self._interaction_repository = interaction_repository
        self.logger = logging.getLogger(__name__)

    async def validate(
        self,
        generated_content_id: str,
        user_id: str,
        interaction_type: InteractionType,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Tuple[InteractionType, Optional[GeneratedContentInteraction]]:
        """
        Validate create content interaction request.

        Args:
            generated_content_id: ID of the generated content
            user_id: ID of the user
            interaction_type: Type of interaction
            metadata: Optional metadata (e.g., report reason)

        Returns:
            Tuple of (validated_interaction_type, existing_interaction_if_applicable)

        Raises:
            ValueError: If interaction_type is invalid or business rules are violated
        """
        # Validate interaction_type
        if not isinstance(interaction_type, InteractionType):
            try:
                interaction_type = InteractionType(interaction_type)
            except ValueError:
                raise ValueError(f"Invalid interaction_type: {interaction_type}")

        # Handle LIKE/DISLIKE mutual exclusivity
        # User can only have one LIKE or DISLIKE entry per content
        if interaction_type in (InteractionType.LIKE, InteractionType.DISLIKE):
            # Check for existing LIKE interaction
            existing_like = self._interaction_repository.get_user_interaction(
                generated_content_id, user_id, InteractionType.LIKE
            )
            
            # Check for existing DISLIKE interaction
            existing_dislike = self._interaction_repository.get_user_interaction(
                generated_content_id, user_id, InteractionType.DISLIKE
            )
            
            # Enforce mutual exclusivity - only one LIKE or DISLIKE should exist
            if existing_like and existing_dislike:
                raise ValueError(
                    f"Data integrity error: Both LIKE and DISLIKE interactions exist for "
                    f"content {generated_content_id} and user {user_id}. "
                    f"This violates mutual exclusivity constraint."
                )
            
            # Get whichever exists (only one can exist due to mutual exclusivity)
            existing_interaction = existing_like or existing_dislike
            
            if existing_interaction:
                # Return existing interaction without modification
                # Service layer will handle type updates
                return interaction_type, existing_interaction
            
            # No existing LIKE/DISLIKE interaction, create new
            return interaction_type, None

        # Check for existing interaction of the same type
        existing_interaction = self._interaction_repository.get_user_interaction(
            generated_content_id, user_id, interaction_type
        )

        # For report and save, enforce one-time rule
        if interaction_type in (InteractionType.REPORT, InteractionType.SAVED):
            if existing_interaction:
                # Return existing interaction without modification
                # Service layer will handle updates
                return interaction_type, existing_interaction

        return interaction_type, None

