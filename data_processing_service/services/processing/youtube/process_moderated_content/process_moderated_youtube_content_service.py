"""
Service for processing moderated YouTube content for users.
"""

import logging
from copy import deepcopy
from datetime import datetime

from data_collector_service.models.user_collected_content import (
    ContentStatus, ContentSubStatus, ContentType)
from data_processing_service.repositories.user_content_repository import \
    UserContentRepository
from data_processing_service.service_context import \
    DataProcessingServiceContext
from data_processing_service.services.processing.youtube.process_moderated_content.metrics_processor.process_moderated_content_metrics_processor import \
    ProcessModeratedContentMetricsProcessor
from data_processing_service.services.processing.youtube.process_moderated_content.subtitles.process_subtitles_for_youtube_content import \
    ProcessSubtitlesForYoutubeContent
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

        # Initialize service context and metrics processor
        self.service_context = DataProcessingServiceContext(
            ProcessModeratedContentMetricsProcessor
        )
        self.metrics_processor = self.service_context.get_metrics_processor()

        # Initialize subtitle processor with service context
        self.subtitle_processor = ProcessSubtitlesForYoutubeContent(
            self.service_context
        )
        self.logger = logging.getLogger(__name__)

    def process(self, user: User) -> None:
        """
        Process moderated YouTube content for a specific user.
        We will basically download the subtitles for these entries and then store them in an ephemeral storage
        Args:
            user: The user object containing configuration and preferences
        """
        try:
            content_to_process_list = (
                self.user_content_repository.get_user_collected_content(
                    user_id=user.id,
                    content_type=ContentType.YOUTUBE_VIDEO,
                    status=ContentStatus.PROCESSING,
                    sub_status=ContentSubStatus.MODERATION_PASSED,
                )
            )
            print(f"Found {len(content_to_process_list)} items to process")

            # Record total content considered
            if self.metrics_processor:
                self.metrics_processor.record_content_considered(
                    len(content_to_process_list)
                )

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
                        updated_content.set_sub_status(
                            ContentSubStatus.SUBTITLES_STORED
                        )

                        # Record successful processing
                        if self.metrics_processor:
                            self.metrics_processor.record_successful_processing(
                                content_to_process.id
                            )

                        # Add it to contents_with_subtitles_stored list
                        contents_with_subtitles_stored.append(updated_content)
                        self.user_content_repository.update_user_collected_content(
                            updated_content
                        )
                    else:
                        # Record processing failure
                        if self.metrics_processor:
                            self.metrics_processor.record_processing_failure(
                                content_to_process.id, "Subtitle processing failed"
                            )
                        # If subtitle processing failed, log it but continue with other content
                        self.logger.warning(
                            f"Failed to process subtitles for content ID: {content_to_process.id}"
                        )

                except Exception as e:
                    # Record processing failure
                    if self.metrics_processor:
                        self.metrics_processor.record_processing_failure(
                            content_to_process.id, str(e)
                        )
                    # Put this whole thing in a try catch to make sure that some issue does not interrupt the flow for other objects, log the issue accordingly
                    self.logger.error(
                        f"Error processing subtitles for content ID {content_to_process.id}: {str(e)}"
                    )
                    continue

            # Complete metrics collection
            if self.metrics_processor:
                self.metrics_processor.complete(success=True)
                self.metrics_processor.print_enhanced_metrics_summary()

        except Exception as e:
            # Complete metrics collection with error
            if self.metrics_processor:
                self.metrics_processor.complete(success=False, error_message=str(e))
            raise

        # Update all successfully processed content
        if contents_with_subtitles_stored:
            print(
                f"Successfully updated {len(contents_with_subtitles_stored)} items out of {len(content_to_process_list)}"
            )
        else:
            print(f"No items were successfully updated")
