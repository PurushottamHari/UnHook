import logging

from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseCommandRouter, Command
from commons.messaging.aggregated_schedule import AggregatedScheduleService
from data_processing_service.messaging.models.commands import (
    CategorizeGeneratedYoutubeContentAggregationCommand,
    StartDataProcessingForUserCollectedContentCommand)
from data_processing_service.services.processing.start_data_processing_service import \
    StartDataProcessingService
from data_processing_service.services.processing.youtube.categorize_content.categorize_youtube_content_aggregation_service import \
    CategorizeYoutubeContentAggregationService

logger = logging.getLogger(__name__)


@injectable()
class CommandRouter(BaseCommandRouter):
    """Routes incoming commands to the appropriate service logic."""

    @inject
    def __init__(
        self,
        aggregated_schedule_service: AggregatedScheduleService,
        start_data_processing_service: StartDataProcessingService,
        categorize_youtube_content_aggregation_service: CategorizeYoutubeContentAggregationService,
    ):
        super().__init__(aggregated_schedule_service)
        self.start_data_processing_service = start_data_processing_service
        self.categorize_youtube_content_aggregation_service = (
            categorize_youtube_content_aggregation_service
        )

    async def handle_domain_command(self, command: Command):
        """Dispatches the command based on action_name and enforces strict typing."""
        try:
            match command.action_name:
                case StartDataProcessingForUserCollectedContentCommand.ACTION_NAME:
                    print(
                        "🚀 Handling StartDataProcessingForUserCollectedContentCommand"
                    )
                    typed_command = StartDataProcessingForUserCollectedContentCommand(
                        **command.model_dump()
                    )
                    await self.start_data_processing_service.start_processing(
                        user_id=typed_command.payload.user_id,
                        user_collected_content_id=typed_command.payload.user_collected_content_id,
                    )
                    print(
                        "✅ Handled StartDataProcessingForUserCollectedContentCommand"
                    )
                case CategorizeGeneratedYoutubeContentAggregationCommand.ACTION_NAME:
                    print("🚀 Handling CategorizeGeneratedYoutubeContentCommand")
                    typed_command = CategorizeGeneratedYoutubeContentAggregationCommand(
                        **command.model_dump()
                    )
                    await self.categorize_youtube_content_aggregation_service.categorize_batch(
                        generated_content_ids=typed_command.payload.generated_content_ids
                    )
                    print("✅ Handled CategorizeGeneratedYoutubeContentCommand")
                # Add new command handlers here as they are implemented
                case _:
                    raise NotImplementedError(
                        f"Command '{command.action_name}' is unimplemented in CommandRouter"
                    )
        except ValidationError as e:
            logger.error(
                f"❌ [CommandRouter] Validation error for '{command.action_name}': {e}"
            )
            raise ValueError(
                f"Invalid command structure for '{command.action_name}': {e}"
            )
        except Exception as e:
            logger.error(
                f"❌ [CommandRouter] Error handling '{command.action_name}': {e}"
            )
            raise
