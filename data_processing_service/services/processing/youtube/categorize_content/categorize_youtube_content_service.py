import asyncio
import logging
import os
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
from data_processing_service.service_context import \
    DataProcessingServiceContext
from data_processing_service.services.processing.youtube.categorize_content.ai_agent.categorization_agent import \
    CategorizationAgent
from data_processing_service.services.processing.youtube.categorize_content.metrics_processor.categorize_content_metrics_processor import \
    CategorizeContentMetricsProcessor


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

        # Initialize service context and metrics processor
        self.service_context = DataProcessingServiceContext(
            CategorizeContentMetricsProcessor
        )
        self.metrics_processor = self.service_context.get_metrics_processor()

    async def categorize_generated_content(self) -> None:
        """
        Fetch all generated content with status REQUIRED_CONTENT_GENERATED and process them in batches of 5.
        Categorize using the AI agent, deep clone, update timestamp, and set status.
        """
        try:
            generated_content_list = self.user_content_repository.get_generated_content(
                status=GeneratedContentStatus.REQUIRED_CONTENT_GENERATED,
                content_type=ContentType.YOUTUBE_VIDEO,
            )
            print(
                f"Found {len(generated_content_list)} generated content items with status REQUIRED_CONTENT_GENERATED"
            )

            # Record total content considered
            if self.metrics_processor:
                self.metrics_processor.record_content_considered(
                    len(generated_content_list)
                )

            batch_size = 8
            for i in range(0, len(generated_content_list), batch_size):
                batch = generated_content_list[i : i + batch_size]
                print(
                    f"Processing batch {i//batch_size + 1} with {len(batch)} items..."
                )
                try:
                    # Use the agent to categorize
                    categorized_batch = (
                        await self.categorization_agent.categorize_content(batch)
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

                        # Record successful categorization
                        if self.metrics_processor:
                            self.metrics_processor.record_successful_categorization(
                                cloned.id
                            )

                        updated_generated_content_list.append(cloned)
                    # Persist the updated batch
                    self.user_content_repository.update_generated_content_batch(
                        updated_generated_content_list
                    )
                except Exception as e:
                    # Record categorization failure for the batch
                    if self.metrics_processor:
                        for content in batch:
                            self.metrics_processor.record_categorization_failure(
                                content.id, str(e)
                            )
                    self.logger.error(f"Batch categorization failed: {str(e)}")
                    continue

            # Complete metrics collection
            if self.metrics_processor:
                self.metrics_processor.complete(success=True)
                print(
                    f"✅ Categorize content completed. Considered: {self.metrics_processor.get_total_considered()}, "
                    f"Successfully categorized: {self.metrics_processor.get_successfully_categorized_count()}, "
                    f"Failures: {self.metrics_processor.get_categorization_failures_count()}"
                )

        except Exception as e:
            # Complete metrics collection with error
            if self.metrics_processor:
                self.metrics_processor.complete(success=False, error_message=str(e))
            raise


if __name__ == "__main__":
    service = CategorizeYoutubeContentService()
    asyncio.run(service.categorize_generated_content())
