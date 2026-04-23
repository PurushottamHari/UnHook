import logging
from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from data_processing_service.messaging.models.commands import (
    CategorizeGeneratedYoutubeContentAggregationCommand,
    CategorizeGeneratedYoutubeContentAggregationPayload)
from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from data_processing_service.repositories.user_content_repository import \
    UserContentRepository
from data_processing_service.services.processing.youtube.categorize_content.ai_agent.categorization_agent import \
    CategorizationAgent


@injectable()
class CategorizeYoutubeContentAggregationService:
    """Service for categorizing YouTube content in aggregated batches."""

    @inject
    def __init__(
        self,
        user_content_repository: UserContentRepository,
        categorization_agent: CategorizationAgent,
        message_producer: MessageProducer,
    ):
        """
        Initialize the service with dependencies.
        """
        self.user_content_repository = user_content_repository
        self.categorization_agent = categorization_agent
        self.message_producer = message_producer
        self.logger = logging.getLogger(__name__)

    async def categorize_batch(self, generated_content_ids: List[str]) -> None:
        """
        Process a batch of generated content IDs.
        Filters to at most 8 items, processes them, and publishes follow-up commands.
        Remaining IDs are published as a new aggregation command.
        """
        if not generated_content_ids:
            return

        # 1. Filter the batch: take first 8 for processing
        processing_ids = generated_content_ids[:8]
        remaining_ids = generated_content_ids[8:]

        self.logger.info(
            f"🚀 [CategorizeYoutubeContentAggregationService] Processing {len(processing_ids)} items. {len(remaining_ids)} remaining."
        )

        commands_to_publish = []

        try:
            # Fetch generated content objects
            generated_content_list = (
                self.user_content_repository.get_generated_content_by_ids(
                    processing_ids
                )
            )

            if not generated_content_list:
                self.logger.warning(
                    f"⚠️ [CategorizeYoutubeContentAggregationService] No generated content found for IDs: {processing_ids}"
                )
            else:
                # 2. Categorize using AI agent
                categorized_batch = await self.categorization_agent.categorize_content(
                    generated_content_list
                )

                updated_list = []
                for content in categorized_batch:
                    # Update status and increment version for optimistic locking
                    content.set_status(
                        GeneratedContentStatus.CATEGORIZATION_COMPLETED,
                        "Categorization Complete.",
                    )
                    content.version += 1
                    updated_list.append(content)

                    # 3. Create follow-up command (defined later)
                    # Placeholder: Create follow-up commands here when defined
                    # self.logger.info(f"TODO: Create follow-up command for generated content ID: {content.id}")

                # 4. Batch update in repository
                if updated_list:
                    self.user_content_repository.update_generated_content_batch(
                        updated_list
                    )
                    self.logger.info(
                        f"✅ [CategorizeYoutubeContentAggregationService] Successfully updated batch of {len(updated_list)} items."
                    )

        except Exception as e:
            self.logger.error(
                f"❌ [CategorizeYoutubeContentAggregationService] Error processing batch: {e}"
            )
            raise

        # 5. If there are remaining IDs, create a new aggregation command
        if remaining_ids:
            reschedule_command = CategorizeGeneratedYoutubeContentAggregationCommand(
                payload=CategorizeGeneratedYoutubeContentAggregationPayload(
                    generated_content_ids=remaining_ids
                )
            )
            commands_to_publish.append(reschedule_command)

        # 6. Publish all commands in the list
        if commands_to_publish:
            # In a real scenario, the topic might be configurable or derived from command.target_service
            # Using data_processing_service.commands as the default topic for this service's commands
            for cmd in commands_to_publish:
                topic = f"{cmd.target_service}.commands"
                await self.message_producer.send_command(topic, cmd)
                self.logger.info(
                    f"📤 [CategorizeYoutubeContentAggregationService] Published command '{cmd.action_name}' to topic '{topic}'"
                )
