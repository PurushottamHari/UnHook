import logging
from typing import List

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from data_processing_service.config import Config
from data_processing_service.messaging.models.commands import (
    CategorizeGeneratedYoutubeContentAggregationCommand,
    CategorizeGeneratedYoutubeContentAggregationPayload,
    GenerateCompleteYoutubeContentCommand,
    GenerateCompleteYoutubeContentPayload)
from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from data_processing_service.repositories.generated_content_repository import \
    GeneratedContentRepository
from data_processing_service.services.processing.youtube.categorize_content.ai_agent.categorization_agent import \
    CategorizationAgent

logger = logging.getLogger(__name__)


@injectable()
class CategorizeYoutubeContentAggregationService:
    """Service for categorizing YouTube content in aggregated batches."""

    @inject
    def __init__(
        self,
        generated_content_repository: GeneratedContentRepository,
        categorization_agent: CategorizationAgent,
        message_producer: MessageProducer,
        config: Config,
    ):
        """
        Initialize the service with dependencies.
        """
        self.generated_content_repository = generated_content_repository
        self.categorization_agent = categorization_agent
        self.message_producer = message_producer
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def categorize_batch(self, generated_content_ids: List[str]) -> None:
        """
        Process a batch of generated content IDs.
        Filters to at most 8 items, processes them, and publishes follow-up commands.
        Remaining IDs are published as a new aggregation command.
        """
        if not generated_content_ids:
            logger.warning(f"No generated content IDs provided.")
            raise ValueError(f"No generated content IDs provided.")

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
                self.generated_content_repository.get_generated_content_by_ids(
                    processing_ids
                )
            )

            if len(generated_content_list) != len(processing_ids):
                missing_ids = list(
                    set(processing_ids)
                    - {content.id for content in generated_content_list}
                )
                self.logger.error(
                    f"❌ [CategorizeYoutubeContentAggregationService] Could not find contents for IDs: {missing_ids}"
                )
                raise ValueError(f"Could not find contents for IDs: {missing_ids}")

            # Categorize using AI agent
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

                followup_command = GenerateCompleteYoutubeContentCommand(
                    payload=GenerateCompleteYoutubeContentPayload(
                        generated_content_id=content.id
                    )
                )
                commands_to_publish.append(followup_command)

            # Batch update in repository
            if updated_list:
                self.generated_content_repository.update_generated_content_batch(
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

        # If there are remaining IDs, create a new aggregation command
        if remaining_ids:
            self.logger.info(
                f"🔄 [CategorizeYoutubeContentAggregationService] Rescheduling {len(remaining_ids)} items."
            )
            reschedule_command = CategorizeGeneratedYoutubeContentAggregationCommand(
                payload=CategorizeGeneratedYoutubeContentAggregationPayload(
                    generated_content_ids=remaining_ids
                )
            )
            commands_to_publish.append(reschedule_command)

        # Publish all commands in the list
        if commands_to_publish:
            for cmd in commands_to_publish:
                await self.message_producer.send_command(cmd)
                self.logger.info(
                    f"📤 [CategorizeYoutubeContentAggregationService] Published command '{cmd.action_name}' to topic '{self.config.data_processing_service_topic}'"
                )
        else:
            self.logger.info(
                f"[CategorizeYoutubeContentAggregationService] No commands to publish."
            )
