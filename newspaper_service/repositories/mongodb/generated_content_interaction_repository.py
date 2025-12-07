"""
MongoDB implementation of generated content interaction repository.
"""

import logging
from typing import List, Optional, Tuple
from uuid import uuid4

from pymongo.errors import DuplicateKeyError

from ...models.generated_content_interaction import (
    GeneratedContentInteraction, InteractionType)
from ..generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from .adapters.generated_content_interaction_adapter import \
    GeneratedContentInteractionAdapter
from .config.database import MongoDB
from .config.settings import get_mongodb_settings
from .models.generated_content_interaction_db_model import \
    GeneratedContentInteractionDBModel


class MongoDBGeneratedContentInteractionRepository(
    GeneratedContentInteractionRepository
):
    """MongoDB implementation of generated content interaction repository."""

    def __init__(self):
        """Initialize the repository."""
        self.settings = get_mongodb_settings()
        self.database = MongoDB.get_database()
        self.collection = self.database[
            self.settings.GENERATED_CONTENT_INTERACTION_COLLECTION_NAME
        ]
        self.logger = logging.getLogger(__name__)

        # Create unique compound index on (generated_content_id, user_id, interaction_type)
        try:
            self.collection.create_index(
                [("generated_content_id", 1), ("user_id", 1), ("interaction_type", 1)],
                unique=True,
                name="unique_interaction",
            )
            self.logger.info("Created unique index on interaction fields")
        except Exception as e:
            self.logger.warning(f"Index creation warning: {str(e)}")

    def create_generated_content_interaction(
        self, interaction: GeneratedContentInteraction
    ) -> GeneratedContentInteraction:
        """
        Create a new interaction.

        Args:
            interaction: The interaction to create

        Returns:
            The created interaction

        Raises:
            DuplicateKeyError: If interaction already exists
        """
        try:
            # Convert to DB model
            db_model = GeneratedContentInteractionAdapter.to_db_model(interaction)
            interaction_doc = db_model.model_dump(by_alias=True)

            # Insert new interaction
            self.collection.insert_one(interaction_doc)

            self.logger.info(
                f"Created new interaction: {interaction.id} for content {interaction.generated_content_id}"
            )

            return interaction
        except DuplicateKeyError as e:
            self.logger.error(f"Duplicate key error: {str(e)}")
            raise Exception("Interaction already exists") from e
        except Exception as e:
            self.logger.error(f"Error creating interaction: {str(e)}")
            raise

    def update_generated_content_interaction(
        self, interaction: GeneratedContentInteraction
    ) -> GeneratedContentInteraction:
        """
        Update an existing interaction.

        Args:
            interaction: The interaction to update

        Returns:
            The updated interaction
        """
        try:
            # Convert to DB model
            db_model = GeneratedContentInteractionAdapter.to_db_model(interaction)
            interaction_doc = db_model.model_dump(by_alias=True)

            # Update filter
            filter_query = {
                "generated_content_id": interaction.generated_content_id,
                "user_id": interaction.user_id,
                "interaction_type": interaction.interaction_type.value,
            }

            # Remove _id from update doc to avoid overwriting it
            if "_id" in interaction_doc:
                del interaction_doc["_id"]

            # Update the interaction (no upsert - must exist)
            result = self.collection.update_one(
                filter_query, {"$set": interaction_doc}
            )

            if result.matched_count == 0:
                raise ValueError(
                    f"Interaction not found for content {interaction.generated_content_id}, "
                    f"user {interaction.user_id}, type {interaction.interaction_type.value}"
                )

            self.logger.info(
                f"Updated existing interaction for content {interaction.generated_content_id}"
            )

            return interaction
        except Exception as e:
            self.logger.error(f"Error updating interaction: {str(e)}")
            raise

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

        Raises:
            ValueError: If more than one interaction is found (data integrity issue)
        """
        try:
            query = {
                "generated_content_id": generated_content_id,
                "user_id": user_id,
                "interaction_type": interaction_type.value,
            }
            
            # Fetch up to 2 items to check for duplicates
            documents = list(self.collection.find(query).limit(2))
            
            if len(documents) == 0:
                return None
            
            if len(documents) > 1:
                self.logger.error(
                    f"Data integrity error: Found {len(documents)} interactions for "
                    f"content {generated_content_id}, user {user_id}, type {interaction_type.value}. "
                    f"Expected at most 1."
                )
                raise ValueError(
                    f"Data integrity error: Multiple interactions found for "
                    f"content {generated_content_id}, user {user_id}, type {interaction_type.value}"
                )
            
            # Exactly one document found
            document = documents[0]
            db_model = GeneratedContentInteractionDBModel(**document)
            return GeneratedContentInteractionAdapter.to_internal_model(db_model)
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(
                f"Error getting user interaction: {str(e)}"
            )
            raise

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
        try:
            # Build query filter
            query = {"generated_content_id": generated_content_id}
            
            # Add cursor filter if starting_after is provided
            # Since we're sorting descending, we want IDs less than starting_after
            if starting_after:
                query["_id"] = {"$lt": starting_after}
            
            # Fetch page_limit + 1 items to determine hasNext
            cursor = (
                self.collection.find(query)
                .sort("_id", -1)  # Sort descending by _id
                .limit(page_limit + 1)
            )
            
            documents = list(cursor)
            has_next = len(documents) > page_limit
            
            # Return only the first page_limit items
            documents_to_return = documents[:page_limit]
            
            interactions = []
            for document in documents_to_return:
                db_model = GeneratedContentInteractionDBModel(**document)
                interactions.append(
                    GeneratedContentInteractionAdapter.to_internal_model(db_model)
                )
            
            return interactions, has_next
        except Exception as e:
            self.logger.error(
                f"Error listing interactions for content {generated_content_id}: {str(e)}"
            )
            raise

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
        try:
            # Build query filter
            query = {"user_id": user_id}
            if interaction_type:
                query["interaction_type"] = interaction_type.value
            
            # Add cursor filter if starting_after is provided
            # Since we're sorting descending, we want IDs less than starting_after
            if starting_after:
                query["_id"] = {"$lt": starting_after}

            # Fetch page_limit + 1 items to determine hasNext
            cursor = (
                self.collection.find(query)
                .sort("_id", -1)  # Sort descending by _id
                .limit(page_limit + 1)
            )
            
            documents = list(cursor)
            has_next = len(documents) > page_limit
            
            # Return only the first page_limit items
            documents_to_return = documents[:page_limit]
            
            interactions = []
            for document in documents_to_return:
                db_model = GeneratedContentInteractionDBModel(**document)
                interactions.append(
                    GeneratedContentInteractionAdapter.to_internal_model(db_model)
                )
            
            return interactions, has_next
        except Exception as e:
            self.logger.error(
                f"Error listing user interactions for user {user_id}: {str(e)}"
            )
            raise

