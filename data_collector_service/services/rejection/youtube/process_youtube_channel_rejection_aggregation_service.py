import copy
import logging
from datetime import datetime
from typing import List, Tuple

from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.config.config import Config
from data_collector_service.external.user_service.client import \
    UserServiceClient
from data_collector_service.messaging.models.commands import (
    ProcessYoutubeChannelRejectionAggregationCommand,
    ProcessYoutubeChannelRejectionAggregationPayload,
    SubmitModeratedContentForProcessingCommand,
    SubmitModeratedContentForProcessingPayload)
from data_collector_service.messaging.redis.producer import \
    RedisMessageProducer
from data_collector_service.models.enums import ContentType
from data_collector_service.models.user_collected_content import (
    ContentStatus, UserCollectedContent)
from data_collector_service.repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from data_collector_service.repositories.youtube_collected_content_repository import \
    YouTubeCollectedContentRepository

from .ai_agent import ContentModerator
from .ai_agent.adaptors.input_adaptor import InputAdaptor
from .rejection_content_service_youtube import get_content_by_video_id

logger = logging.getLogger(__name__)


@injectable()
class ProcessYoutubeChannelRejectionAggregationService:
    """Service for processing aggregated YouTube content rejection."""

    @inject
    def __init__(
        self,
        user_service_client: UserServiceClient,
        content_repository: UserCollectedContentRepository,
        youtube_repository: YouTubeCollectedContentRepository,
        moderator_agent: ContentModerator,
        message_producer: RedisMessageProducer,
        config: Config,
    ):
        """
        Initialize the service.

        Args:
            user_service_client: Client for user service
            content_repository: Repository for user collected content
            youtube_repository: Repository for YouTube raw content
            moderator_agent: Content moderator agent
            message_producer: Message producer for enqueuing commands
            config: Application configuration
        """
        self.user_service_client = user_service_client
        self.content_repository = content_repository
        self.youtube_repository = youtube_repository
        self.moderator_agent = moderator_agent
        self.message_producer = message_producer
        self.config = config

    async def process_channel(
        self, user_id: str, channel_name: str, content_ids: List[str]
    ) -> None:
        """
        Process a batch of YouTube content for rejection.

        Args:
            user_id: The ID of the user
            channel_name: The name of the YouTube channel
            content_ids: List of content IDs to process
        """
        print(
            f"🎬 [ProcessYoutubeChannelRejectionAggregationService] Processing {len(content_ids)} items for channel: {channel_name}"
        )

        # 1. Fetch User and Content Objects
        user = await self.user_service_client.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found.")
            raise ValueError(f"User {user_id} not found.")

        if len(content_ids) == 0:
            logger.warning(f"No content IDs provided for user {user_id}")
            raise ValueError(f"No content IDs provided for user {user_id}")

        contents = self.content_repository.get_content_by_ids(content_ids)
        if len(contents) != len(content_ids):
            missing_ids = list(set(content_ids) - {content.id for content in contents})
            logger.error(
                f"❌ [ProcessYoutubeChannelRejectionAggregationService] Could not find contents for IDs: {missing_ids}"
            )
            raise ValueError(f"Could not find contents for IDs: {missing_ids}")

        # 2. Partition Content
        collected = [c for c in contents if c.status == ContentStatus.COLLECTED]
        accepted = [c for c in contents if c.status == ContentStatus.ACCEPTED]

        # 3. Check Rejection Criteria
        manual_config = next(
            (
                c
                for c in user.manual_configs.youtube.channels
                if c.channel_id == channel_name
            ),
            None,
        )
        criteria = (
            manual_config.not_interested
            if manual_config and manual_config.not_interested
            else user.not_interested
        )

        newly_accepted = []
        newly_rejected = []
        remaining_ids = []

        if not criteria:
            print(
                f"ℹ️ [ProcessYoutubeChannelRejectionAggregationService] No criteria for channel {channel_name}, accepting all collected content."
            )
            for content in collected:
                updated = copy.deepcopy(content)
                updated.set_status(
                    ContentStatus.ACCEPTED, "No rejection criteria defined."
                )
                updated.version += 1  # Explicit version increment
                newly_accepted.append(updated)
        else:
            # Limit evaluation to 15 videos
            to_evaluate = collected[:15]
            evaluate_later = collected[15:]
            remaining_ids = [content.id for content in evaluate_later]

            if to_evaluate:
                print(
                    f"🔍 [ProcessYoutubeChannelRejectionAggregationService] Evaluating {len(to_evaluate)} videos for channel {channel_name}"
                )

                # Fetch video details from repository
                video_ids = [content.external_id for content in to_evaluate]
                youtube_video_details_list = self.youtube_repository.get_videos_by_ids(
                    video_ids
                )

                if len(youtube_video_details_list) != len(to_evaluate):
                    print(
                        f"⚠️ [ProcessYoutubeChannelRejectionAggregationService] Mismatch in video details count: expected {len(to_evaluate)}, found {len(youtube_video_details_list)}"
                    )

                mod_input = InputAdaptor.to_moderation_input(
                    not_interested_list=criteria,
                    youtube_video_details_list=youtube_video_details_list,
                )
                moderation_output = await self.moderator_agent.moderate_content(
                    moderation_input=mod_input
                )

                rejected_with_reasons = get_content_by_video_id(
                    moderation_output, to_evaluate
                )
                rejected_ids = {content.id for content, _ in rejected_with_reasons}
                rejected_map = {
                    content.id: reason for content, reason in rejected_with_reasons
                }

                for content in to_evaluate:
                    updated = copy.deepcopy(content)
                    if content.id in rejected_ids:
                        updated.set_status(
                            ContentStatus.REJECTED, rejected_map[content.id]
                        )
                        updated.version += 1
                        newly_rejected.append(updated)
                    else:
                        updated.set_status(ContentStatus.ACCEPTED, "Moderation passed.")
                        updated.version += 1
                        newly_accepted.append(updated)

        # 4. Bulk DB Update
        all_modified = newly_accepted + newly_rejected
        if all_modified:
            self.content_repository.upsert_user_collected_content_batch(all_modified)
            print(
                f"✅ [ProcessYoutubeChannelRejectionAggregationService] Upserted {len(all_modified)} items to database."
            )

        # 5. Construct Commands to Send
        commands_to_send = []

        # Messaging Skeleton for accepted content
        all_accepted_for_next_stage = accepted + newly_accepted
        for content in all_accepted_for_next_stage:
            command = SubmitModeratedContentForProcessingCommand(
                payload=SubmitModeratedContentForProcessingPayload(
                    user_id=user_id,
                    user_collected_content_id=content.id,
                )
            )
            commands_to_send.append(command)

        # Schedule Next Batch if needed
        if remaining_ids:
            print(
                f"⏳ [ProcessYoutubeChannelRejectionAggregationService] Enqueuing next batch for {len(remaining_ids)} remaining items."
            )
            payload = ProcessYoutubeChannelRejectionAggregationPayload(
                user_id=user_id,
                channel_name=channel_name,
                user_collected_content_ids=remaining_ids,
            )
            next_batch_command = ProcessYoutubeChannelRejectionAggregationCommand(
                payload=payload
            )
            commands_to_send.append(next_batch_command)

        # 6. Batch Fire Publish Service
        if commands_to_send:
            await self.message_producer.send_commands(commands_to_send)
            print(
                f"🚀 [ProcessYoutubeChannelRejectionAggregationService] Published {len(commands_to_send)} commands."
            )
