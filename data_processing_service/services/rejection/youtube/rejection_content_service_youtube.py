"""
Service for handling YouTube content rejection.
"""

import copy
from datetime import datetime
from typing import List, Tuple

from data_collector_service.collectors.youtube.models.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_collector_service.models.enums import ContentType
from data_collector_service.models.user_collected_content import (
    ContentStatus,
    ContentSubStatus,
    UserCollectedContent,
)
from user_service.models.user import User

from .ai_agent import ContentModerator
from .ai_agent.adaptors.input_adaptor import InputAdaptor
from .ai_agent.models import ModerationOutput


class RejectionContentServiceYoutube:
    """Service for handling YouTube content rejection."""

    def __init__(self, moderator_agent: ContentModerator):
        """
        Initialize the service.

        Args:
            user_service_client: Client for user service
            user_content_repository: Repository for user content
        """
        self.moderator_agent = moderator_agent

    async def reject(
        self, user: User, contents: List[UserCollectedContent]
    ) -> List[UserCollectedContent]:
        """
        Reject YouTube content for a user.

        Args:
            user: The user object
            contents: The unprocessed content to reject
        """
        final_moderated_content_list = []
        yotube_manual_channel_list = user.manual_configs.youtube.channels
        all_rejected_ids = set()
        # Group contents by channel_name
        channel_ydlist_map = {}
        for content in contents:
            youtube_video_details = content.data.get(ContentType.YOUTUBE_VIDEO)
            if not isinstance(youtube_video_details, YouTubeVideoDetails):
                raise TypeError(
                    "The 'YOUTUBE_VIDEO' content data must be a YouTubeVideoDetails object, "
                    f"but got {type(youtube_video_details).__name__} instead."
                )
            channel_name = youtube_video_details.channel_name
            if channel_name not in channel_ydlist_map:
                channel_ydlist_map[channel_name] = []
            channel_ydlist_map[channel_name].append(youtube_video_details)
        # Now channel_map is {channel_name: [UserCollectedContent, ...]}
        # You can process each channel's contents as needed
        for channel_name, ydlist in channel_ydlist_map.items():
            print(f"Processing {len(ydlist)} items for channel: {channel_name}")
            if not ydlist:
                continue
            youtube_manual_channel = next(
                (
                    manual_channel
                    for manual_channel in yotube_manual_channel_list
                    if manual_channel.channel_id == channel_name
                ),
                None,
            )
            not_interested = None
            if (
                youtube_manual_channel
                and len(youtube_manual_channel.not_interested) != 0
            ):
                not_interested = youtube_manual_channel.not_interested
            elif not youtube_manual_channel and len(user.not_interested) != 0:
                not_interested = user.not_interested

            if not_interested:
                moderation_input = InputAdaptor.to_moderation_input(
                    not_interested_list=youtube_manual_channel.not_interested,
                    youtube_video_details_list=ydlist,
                )
                moderation_output = await self.moderator_agent.moderate_content(
                    moderation_input=moderation_input
                )
                rejected_content_with_reasons = get_content_by_video_id(
                    moderation_output, contents
                )
                print(f"Rejected {len(moderation_output.rejected_items)} items")
                for rejected_content, reason in rejected_content_with_reasons:
                    all_rejected_ids.add(rejected_content.id)
                    updated_rejected_content = copy.deepcopy(rejected_content)
                    updated_rejected_content.updated_at = datetime.utcnow()
                    updated_rejected_content.status = ContentStatus.REJECTED
                    updated_rejected_content.add_status_detail(
                        ContentStatus.REJECTED, reason
                    )
                    final_moderated_content_list.append(updated_rejected_content)
        # After all channel processing, update non-rejected content as PROCESSED
        # We should also make the sub_status as MODERATION_PASSED
        for content in contents:
            if content.id not in all_rejected_ids:
                updated_processed_content = copy.deepcopy(content)
                updated_processed_content.updated_at = datetime.utcnow()
                updated_processed_content.status = ContentStatus.PROCESSING
                updated_processed_content.add_status_detail(
                    ContentStatus.PROCESSING, "Moderation passed."
                )
                updated_processed_content.sub_status = (
                    ContentSubStatus.MODERATION_PASSED
                )
                updated_processed_content.add_sub_status_detail(
                    ContentSubStatus.MODERATION_PASSED, "first moderation passed"
                )
                final_moderated_content_list.append(updated_processed_content)
        return final_moderated_content_list


def get_content_by_video_id(
    moderation_output: ModerationOutput, contents: List[UserCollectedContent]
) -> List[Tuple[UserCollectedContent, str]]:
    """
    Given a ModerationOutput and a list of UserCollectedContent, return a list of tuples (UserCollectedContent, reason)
    whose external_id matches any id in moderation_output.rejected_items, along with the rejection reason.

    Returns:
        List[Tuple[UserCollectedContent, str]]: Each tuple contains a UserCollectedContent object and the corresponding rejection reason string.
    """
    # Map rejected id to reason
    id_to_reason = {item.id: item.reason for item in moderation_output.rejected_items}
    result = []
    for content in contents:
        if content.external_id in id_to_reason:
            result.append((content, id_to_reason[content.external_id]))
    return result
