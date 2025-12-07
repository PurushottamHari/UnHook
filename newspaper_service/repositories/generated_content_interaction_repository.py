"""
Abstract base class for generated content interaction repository.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from ..models.generated_content_interaction import (
    GeneratedContentInteraction, InteractionType)


class GeneratedContentInteractionRepository(ABC):
    """Abstract interface for generated content interaction repository operations."""

    @abstractmethod
    def create_generated_content_interaction(
        self, interaction: GeneratedContentInteraction
    ) -> GeneratedContentInteraction:
        """
        Create a new interaction.

        Args:
            interaction: The interaction to create

        Returns:
            The created interaction
        """
        pass

    @abstractmethod
    def update_generated_content_interaction(
        self,
        interaction: GeneratedContentInteraction,
        override_interaction_type: Optional[InteractionType] = None,
    ) -> GeneratedContentInteraction:
        """
        Update an existing interaction.

        Args:
            interaction: The interaction to update
            override_interaction_type: Optional interaction type to use for filtering.
                If provided, filters by this type instead of interaction.interaction_type.
                Useful for converting LIKE to DISLIKE or vice versa.

        Returns:
            The updated interaction
        """
        pass

    @abstractmethod
    def get_user_interaction(
        self,
        generated_content_id: str,
        user_id: str,
        interaction_type: InteractionType,
    ) -> Optional[GeneratedContentInteraction]:
        """
        Get a specific user interaction for content by type.

        Args:
            generated_content_id: ID of the generated content
            user_id: ID of the user
            interaction_type: Type of interaction to retrieve

        Returns:
            The interaction if found, None otherwise
        """
        pass

    @abstractmethod
    def list_user_interactions_for_content(
        self,
        generated_content_id: str,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> Tuple[List[GeneratedContentInteraction], bool]:
        """
        List interactions for specific content with pagination.

        Args:
            generated_content_id: ID of the generated content
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return

        Returns:
            Tuple of (list of interactions, has_next) where has_next indicates if more items exist
        """
        pass

    @abstractmethod
    def list_user_interactions(
        self,
        user_id: str,
        interaction_type: Optional[InteractionType] = None,
        starting_after: Optional[str] = None,
        page_limit: int = 10,
    ) -> Tuple[List[GeneratedContentInteraction], bool]:
        """
        List user's interactions with pagination, optionally filtered by type.

        Args:
            user_id: ID of the user
            interaction_type: Optional filter by interaction type
            starting_after: Optional cursor ID to start after (for pagination)
            page_limit: Maximum number of items to return

        Returns:
            Tuple of (list of interactions, has_next) where has_next indicates if more items exist
        """
        pass

    @abstractmethod
    def get_active_interactions_by_generated_content_ids(
        self,
        user_id: str,
        generated_content_ids: List[str],
    ) -> Dict[str, List[GeneratedContentInteraction]]:
        """
        Get active interactions for multiple generated content IDs for a specific user.

        Args:
            user_id: ID of the user
            generated_content_ids: List of generated content IDs (MongoDB _id)

        Returns:
            Dictionary mapping generated_content_id to list of active interactions
        """
        pass
