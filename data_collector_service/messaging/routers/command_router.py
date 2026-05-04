from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseCommandRouter, Command
from commons.messaging.aggregated_schedule import AggregatedScheduleService
from data_collector_service.messaging.models.commands import (
    CollectYouTubeChannelForUserCommand, EnrichYouTubeVideoForUserCommand,
    ProcessYoutubeChannelRejectionAggregationCommand,
    StartUserCollectionCommand, SubmitModeratedContentForProcessingCommand)
from data_collector_service.services.collection.start_user_collection_service import \
    StartUserCollectionService
from data_collector_service.services.collection.youtube.collect_youtube_content_service import \
    CollectYouTubeContentService
from data_collector_service.services.collection.youtube.enrich_youtube_video_content_service import \
    EnrichYouTubeVideoContentService
from data_collector_service.services.rejection.reject_content_service import \
    RejectContentService
from data_collector_service.services.rejection.youtube.process_youtube_channel_rejection_aggregation_service import \
    ProcessYoutubeChannelRejectionAggregationService
from data_collector_service.services.submit.submit_for_processing_service import \
    SubmitForProcessingService


@injectable()
class CommandRouter(BaseCommandRouter):
    """Routes incoming commands to the appropriate service logic."""

    @inject
    def __init__(
        self,
        start_user_collection_service: StartUserCollectionService,
        collect_youtube_content_service: CollectYouTubeContentService,
        reject_content_service: RejectContentService,
        enrich_youtube_video_content_service: EnrichYouTubeVideoContentService,
        process_youtube_channel_rejection_aggregation_service: ProcessYoutubeChannelRejectionAggregationService,
        submit_for_processing_service: SubmitForProcessingService,
        aggregated_schedule_service: AggregatedScheduleService,
    ):
        super().__init__(aggregated_schedule_service)
        self.start_user_collection_service = start_user_collection_service
        self.collect_youtube_content_service = collect_youtube_content_service
        self.reject_content_service = reject_content_service
        self.enrich_youtube_video_content_service = enrich_youtube_video_content_service
        self.process_youtube_channel_rejection_aggregation_service = (
            process_youtube_channel_rejection_aggregation_service
        )
        self.submit_for_processing_service = submit_for_processing_service

    async def handle_domain_command(self, command: Command):
        """Dispatches the command based on action_name and enforces strict typing."""
        try:
            match command.action_name:
                case StartUserCollectionCommand.ACTION_NAME:
                    # Cast and validate the specific command model
                    start_command = StartUserCollectionCommand.model_validate(
                        command.model_dump()
                    )
                    print(f"🎬 [CommandRouter] Starting {start_command.action_name}")
                    await self.start_user_collection_service.start_collection(
                        start_command.payload.user_id
                    )
                    print(f"✅ [CommandRouter] {start_command.action_name} completed")

                case CollectYouTubeChannelForUserCommand.ACTION_NAME:
                    # Cast and validate the granular channel command
                    channel_command = (
                        CollectYouTubeChannelForUserCommand.model_validate(
                            command.model_dump()
                        )
                    )
                    print(f"🎬 [CommandRouter] Processing youtube channel collection")

                    await self.collect_youtube_content_service.collect_channel(
                        user_id=channel_command.payload.user_id,
                        channel_id=channel_command.payload.channel_id,
                        max_videos=channel_command.payload.max_videos,
                    )
                    print(
                        f"✅ [CommandRouter] Channel {channel_command.payload.channel_id} collection completed"
                    )

                case EnrichYouTubeVideoForUserCommand.ACTION_NAME:
                    # Cast and validate the granular video command
                    video_command = EnrichYouTubeVideoForUserCommand.model_validate(
                        command.model_dump()
                    )

                    print(f"🎬 [CommandRouter] Processing youtube video enrichment")

                    await self.enrich_youtube_video_content_service.enrich_video(
                        video_id=video_command.payload.video_id,
                        user_id=video_command.payload.user_id,
                        user_collected_content_id=video_command.payload.user_collected_content_id,
                        channel_name=video_command.payload.channel_name,
                    )

                    print(
                        f"✅ [CommandRouter] Video {video_command.payload.video_id} enrichment completed"
                    )

                case ProcessYoutubeChannelRejectionAggregationCommand.ACTION_NAME:
                    # Cast and validate the granular channel command
                    channel_command = (
                        ProcessYoutubeChannelRejectionAggregationCommand.model_validate(
                            command.model_dump()
                        )
                    )
                    print(f"🎬 [CommandRouter] Processing youtube channel rejection")

                    await self.process_youtube_channel_rejection_aggregation_service.process_channel(
                        user_id=channel_command.payload.user_id,
                        channel_name=channel_command.payload.channel_name,
                        content_ids=channel_command.payload.user_collected_content_ids,
                    )
                    print(
                        f"✅ [CommandRouter] Channel {channel_command.payload.channel_name} rejection processed"
                    )

                case SubmitModeratedContentForProcessingCommand.ACTION_NAME:
                    # Cast and validate the granular channel command
                    submit_command = (
                        SubmitModeratedContentForProcessingCommand.model_validate(
                            command.model_dump()
                        )
                    )
                    print(
                        f"🎬 [CommandRouter] Processing submit moderated content for processing"
                    )

                    await self.submit_for_processing_service.submit_for_processing(
                        user_id=submit_command.payload.user_id,
                        user_collected_content_id=submit_command.payload.user_collected_content_id,
                    )

                    print(
                        f"✅ [CommandRouter] Submit moderated content for processing completed"
                    )

                case _:
                    raise NotImplementedError(
                        f"Command '{command.action_name}' is unimplemented in CommandRouter"
                    )
        except ValidationError as e:
            print(
                f"❌ [CommandRouter] Validation error for '{command.action_name}': {e}"
            )
            raise ValueError(
                f"Invalid command structure for '{command.action_name}': {e}"
            )
        except Exception as e:
            print(f"❌ [CommandRouter] Error handling '{command.action_name}': {e}")
            raise
