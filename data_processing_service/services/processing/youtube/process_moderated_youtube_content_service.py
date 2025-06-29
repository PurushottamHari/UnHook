"""
Service for processing moderated YouTube content for users.
"""

import logging
from copy import deepcopy
from datetime import datetime

from data_collector_service.models.user_collected_content import (
    ContentStatus,
    ContentSubStatus,
    ContentType,
)
from data_processing_service.repositories.user_content_repository import (
    UserContentRepository,
)
from data_processing_service.services.processing.youtube.subtitles.process_subtitles_for_youtube_content import (
    ProcessSubtitlesForYoutubeContent,
)
from user_service.models.user import User


class ProcessModeratedYoutubeContentService:
    """Service for processing moderated YouTube content for users."""

    def __init__(self, user_content_repository: UserContentRepository):
        """
        Initialize the service with a user content repository.

        Args:
            user_content_repository: Repository for managing user content data
        """
        self.user_content_repository = user_content_repository
        self.subtitle_processor = ProcessSubtitlesForYoutubeContent()
        self.logger = logging.getLogger(__name__)

    def process(self, user: User) -> None:
        """
        Process moderated YouTube content for a specific user.
        We will basically download the subtitles for these entries and then store them in an ephemeral storage
        Args:
            user: The user object containing configuration and preferences
        """
        content_to_process_list = (
            self.user_content_repository.get_user_collected_content(
                user_id=user.id,
                content_type=ContentType.YOUTUBE_VIDEO,
                status=ContentStatus.PROCESSING,
                sub_status=ContentSubStatus.MODERATION_PASSED,
            )
        )
        print(f"Found {len(content_to_process_list)} items to process")
        contents_with_subtitles_stored = []
        for content_to_process in content_to_process_list:
            try:
                # Process subtitles for this content
                subtitle_processed = self.subtitle_processor.process_subtitles(
                    content_to_process
                )

                if subtitle_processed:
                    # Make a deepcopy of the content_to_process, update the updated_at, sub_status = SUBTITLES_STORED
                    updated_content = deepcopy(content_to_process)
                    updated_content.updated_at = datetime.utcnow()
                    updated_content.sub_status = ContentSubStatus.SUBTITLES_STORED

                    # Add it to contents_with_subtitles_stored list
                    contents_with_subtitles_stored.append(updated_content)
                else:
                    # If subtitle processing failed, log it but continue with other content
                    self.logger.warning(
                        f"Failed to process subtitles for content ID: {content_to_process.id}"
                    )

            except Exception as e:
                # Put this whole thing in a try catch to make sure that some issue does not interrupt the flow for other objects, log the issue accordingly
                self.logger.error(
                    f"Error processing subtitles for content ID {content_to_process.id}: {str(e)}"
                )
                continue

        # Update all successfully processed content
        if contents_with_subtitles_stored:
            print(f"Updating {len(contents_with_subtitles_stored)} items")
            self.user_content_repository.update_user_collected_content_batch(
                updated_user_collected_content_list=contents_with_subtitles_stored
            )
