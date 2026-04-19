from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import Command
from data_collector_service.messaging.models.aggregated_schedule_commands import \
    ProcessYoutubeChannelRejectionAggregationCommand
from data_collector_service.messaging.models.commands import (
    CollectYouTubeChannelForUserCommand, EnrichYouTubeVideoForUserCommand,
    StartUserCollectionCommand)
from data_collector_service.services.collection.start_user_collection_service import \
    StartUserCollectionService
from data_collector_service.services.collection.youtube.collect_youtube_content_service import \
    CollectYouTubeContentService
from data_collector_service.services.collection.youtube.enrich_youtube_video_content_service import \
    EnrichYouTubeVideoContentService
from data_collector_service.services.rejection.reject_content_service import \
    RejectContentService


@injectable()
class CommandRouter:
    """Routes incoming commands to the appropriate service logic."""

    @inject
    def __init__(
        self,
        start_user_collection_service: StartUserCollectionService,
        collect_youtube_content_service: CollectYouTubeContentService,
        reject_content_service: RejectContentService,
        enrich_youtube_video_content_service: EnrichYouTubeVideoContentService,
    ):
        self.start_user_collection_service = start_user_collection_service
        self.collect_youtube_content_service = collect_youtube_content_service
        self.reject_content_service = reject_content_service
        self.enrich_youtube_video_content_service = enrich_youtube_video_content_service

    async def handle(self, command: Command):
        """Dispatches the command based on action_name and enforces strict typing."""
        try:
            match command.action_name:
                case "start_user_collection":
                    # Cast and validate the specific command model
                    start_command = StartUserCollectionCommand.model_validate(
                        command.model_dump()
                    )
                    print(f"🎬 [CommandRouter] Starting {start_command.action_name}")
                    await self.start_user_collection_service.start_collection(
                        start_command.payload.user_id
                    )
                    print(f"✅ [CommandRouter] {start_command.action_name} completed")

                case "collect_youtube_channel_for_user":
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

                case "enrich_youtube_video_for_user":
                    # Cast and validate the granular video command
                    video_command = EnrichYouTubeVideoForUserCommand.model_validate(
                        command.model_dump()
                    )
                    await self.enrich_youtube_video_content_service.enrich_video(
                        video_id=video_command.payload.video_id,
                        user_id=video_command.payload.user_id,
                        user_collected_content_id=video_command.payload.user_collected_content_id,
                    )

                    print(
                        f"✅ [CommandRouter] Video {video_command.payload.video_id} enrichment completed"
                    )

                # case "process_youtube_channel_rejection_aggregation":
                #     # Cast and validate the granular video command
                #     process_youtube_channel_rejection_aggregation_command = (
                #         ProcessYoutubeChannelRejectionAggregationCommand.model_validate(
                #             command.model_dump()
                #         )
                #     )
                #     await self.enrich_youtube_video_content_service.enrich_video(
                #         video_id=process_youtube_channel_rejection_aggregation_command.payload.video_id,
                #         user_id=process_youtube_channel_rejection_aggregation_command.payload.user_id,
                #         user_collected_content_id=process_youtube_channel_rejection_aggregation_command.payload.user_collected_content_id,
                #     )

                #     print(
                #         f"✅ [CommandRouter] Video {process_youtube_channel_rejection_aggregation_command.payload.video_id} enrichment completed"
                #     )

                case "reject_content":
                    print(f"🎬 [CommandRouter] Starting reject_content command")
                    await self.reject_content_service.reject(command.payload["user_id"])
                    print("✅ [CommandRouter] reject_content command completed")

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
