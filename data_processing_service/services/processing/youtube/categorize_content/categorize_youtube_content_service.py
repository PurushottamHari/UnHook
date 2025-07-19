import asyncio
import logging
from copy import deepcopy
from datetime import datetime
from typing import List

from data_collector_service.models.enums import ContentType
from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from data_processing_service.repositories.mongodb.config.database import \
    MongoDB
from data_processing_service.repositories.mongodb.user_content_repository import \
    MongoDBUserContentRepository
from data_processing_service.services.processing.youtube.categorize_content.ai_agent.categorization_agent import \
    CategorizationAgent


class CategorizeYoutubeContentService:
    """Service for categorizing YouTube content for users."""

    def __init__(self):
        # Initialize MongoDB connection if not already connected
        if MongoDB.db is None:
            MongoDB.connect_to_database()
        # Create MongoDB user content repository
        self.user_content_repository = MongoDBUserContentRepository(
            MongoDB.get_database()
        )
        self.logger = logging.getLogger(__name__)
        self.categorization_agent = CategorizationAgent()

    async def categorize_generated_content(self) -> None:
        """
        Fetch all generated content with status REQUIRED_CONTENT_GENERATED and process them in batches of 5.
        Categorize using the AI agent, deep clone, update timestamp, and set status.
        """
        generated_content_list = self.user_content_repository.get_generated_content(
            status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
            content_type=ContentType.YOUTUBE_VIDEO,
        )
        print(
            f"Found {len(generated_content_list)} generated content items with status REQUIRED_CONTENT_GENERATED"
        )

        batch_size = 8
        for i in range(0, len(generated_content_list), batch_size):
            batch = generated_content_list[i : i + batch_size]
            print(f"Processing batch {i//batch_size + 1} with {len(batch)} items...")
            # Use the agent to categorize
            categorized_batch = await self.categorization_agent.categorize_content(
                batch
            )
            updated_generated_content_list = []
            for original, categorized in zip(batch, categorized_batch):
                # Deep clone
                cloned = deepcopy(categorized)
                # Update timestamp and status
                cloned.set_status(
                    GeneratedContentStatus.CATEGORIZATION_COMPLETED,
                    "Categorization Complete.",
                )
                print(
                    f"Categorized content id {cloned.id} with category {cloned.category.category if cloned.category else None}"
                )
                updated_generated_content_list.append(cloned)
            # Persist the updated batch
            self.user_content_repository.update_generated_content_batch(
                updated_generated_content_list
            )


if __name__ == "__main__":
    service = CategorizeYoutubeContentService()
    asyncio.run(service.categorize_generated_content())
