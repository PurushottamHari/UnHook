"""
Service for collating article candidates into a newspaper.
"""

import logging
from datetime import datetime
from typing import List, Tuple

import pytz
from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import MessageProducer
from commons.messaging.contracts.events.newspaper_service.models import (
    CandidateLinksPayload, ContentAddedToNewspaperEvent,
    ContentAddedToNewspaperPayload)
from data_collector_service.models.user_collected_content import (
    ContentType, UserCollectedContent)
from newspaper_service.external.user_service import UserServiceClient
from newspaper_service.models import (CandidateStatus, NewspaperStatus,
                                      NewspaperV2)
from newspaper_service.repositories import (
    GeneratedContentRepository, NewspaperArticleCandidateRepository,
    NewspaperV2Repository, UserCollectedContentRepository)
from user_service.models.enums import CategoryName, Weekday
from user_service.models.user import User


@injectable()
class CollateArticlesForNewspaperService:
    """Service for collating article candidates into a newspaper."""

    @inject
    def __init__(
        self,
        newspaper_repository: NewspaperV2Repository,
        candidate_repository: NewspaperArticleCandidateRepository,
        user_content_repository: UserCollectedContentRepository,
        generated_content_repository: GeneratedContentRepository,
        user_service_client: UserServiceClient,
        message_producer: MessageProducer,
    ):
        self.newspaper_repository = newspaper_repository
        self.candidate_repository = candidate_repository
        self.user_content_repository = user_content_repository
        self.generated_content_repository = generated_content_repository
        self.user_service_client = user_service_client
        self.message_producer = message_producer
        self.logger = logging.getLogger(__name__)

    async def execute(self, user_id: str, newspaper_id: str) -> None:
        """
        Execute the collation process for a newspaper.
        """
        self.logger.info(
            f"🚀 Starting collation for newspaper {newspaper_id} (User: {user_id})"
        )

        # Validate newspaper
        newspaper = self.newspaper_repository.get_by_id(newspaper_id)
        if not newspaper:
            raise ValueError(f"Newspaper {newspaper_id} not found")

        if newspaper.user_id != user_id:
            raise ValueError(
                f"Newspaper {newspaper_id} does not belong to user {user_id}"
            )

        # Get user preferences for filtering
        user = self.user_service_client.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # if newspaper.status != NewspaperStatus.COLLATING:
        #     raise ValueError(f"Newspaper {newspaper_id} is in status {newspaper.status}, expected COLLATING")

        # Fetch candidates in CONSIDERED status
        candidates = self.candidate_repository.list_candidates_by_user_and_status(
            user_id, CandidateStatus.CONSIDERED
        )

        if not candidates:
            self.logger.info(f"No candidates in CONSIDERED status for user {user_id}")
            return

        # We use today's date for collation scope
        today = datetime.now(pytz.UTC)
        allowed_categories, scheduled_channels = self._get_scheduled_criteria_for_date(
            user, today
        )

        # Filter candidates based on preferences
        filtered_candidates = await self._filter_candidates(
            candidates, allowed_categories, scheduled_channels
        )

        if not filtered_candidates:
            self.logger.info(
                f"No candidates fit the scope for today's date ({today.date()})"
            )
            return

        # Update candidates and prepare events
        events = []
        for candidate in filtered_candidates:
            candidate.newspaper_id = newspaper_id
            candidate.set_status(
                CandidateStatus.USED, f"Added to newspaper {newspaper_id}"
            )
            candidate.version += 1
            # further entricasies will be flushed out later

            # Prepare event payload
            links_payload = CandidateLinksPayload(
                user_collected_content_id=candidate.links.user_collected_content_id,
                generated_content_id=candidate.links.generated_content_id,
                generated_content_id_list=candidate.links.generated_content_id_list,
            )

            events.append(
                ContentAddedToNewspaperEvent(
                    topic="newspaper_service:events",
                    payload=ContentAddedToNewspaperPayload(
                        newspaper_id=newspaper_id,
                        linked_id=candidate.linked_id,
                        links=links_payload,
                    ),
                )
            )

        # Bulk update candidates
        self.candidate_repository.upsert_candidates(filtered_candidates)
        self.logger.info(
            f"✅ Updated {len(filtered_candidates)} candidates to USED status"
        )

        # One-shot event publishing
        await self.message_producer.publish_events(events)
        self.logger.info(
            f"📡 Published {len(events)} ContentAddedToNewspaperEvent events"
        )

    async def _filter_candidates(
        self,
        candidates: List,
        allowed_categories: List[CategoryName],
        scheduled_channels: List[str],
    ) -> List:
        """Filter candidates based on categories and channels."""
        # For now, we only handle USER_COLLECTED_CONTENT sources
        # We need to fetch the actual content to check categories/channels

        # 1. Fetch all UserCollectedContent for the candidates
        user_content_ids = [c.linked_id for c in candidates]
        # This is a bit inefficient if done one by one, but let's assume we have a way to fetch multiple or just do it for now
        # Actually, let's see if there is a bulk fetch

        # If no bulk fetch, we do it one by one (or fix the repo later)
        processed_content_list = []
        for content_id in user_content_ids:
            content = self.user_content_repository.get_content_by_id(content_id)
            if content:
                processed_content_list.append(content)

        if not processed_content_list:
            return []

        # 2. Filter by categories using generated content repository
        external_ids = [content.external_id for content in processed_content_list]
        category_matched_external_ids = (
            self.generated_content_repository.filter_external_ids_by_criteria(
                external_ids=external_ids,
                categories=allowed_categories,
                youtube_channels=scheduled_channels,
            )
        )

        # 3. Filter by channels directly
        channel_matched_external_ids = []
        if scheduled_channels:
            for content in processed_content_list:
                if content.content_type == ContentType.YOUTUBE_VIDEO:
                    video_details = content.data.get(ContentType.YOUTUBE_VIDEO)
                    if (
                        video_details
                        and hasattr(video_details, "channel_id")
                        and video_details.channel_id in scheduled_channels
                    ):
                        channel_matched_external_ids.append(content.external_id)

        # 4. Union of matches
        all_matching_external_ids = set(category_matched_external_ids) | set(
            channel_matched_external_ids
        )

        # Filter candidates by matching external IDs
        filtered_candidates = []
        content_id_to_external_id = {
            c.id: c.external_id for c in processed_content_list
        }

        for candidate in candidates:
            external_id = content_id_to_external_id.get(candidate.linked_id)
            if external_id in all_matching_external_ids:
                filtered_candidates.append(candidate)

        return filtered_candidates

    def _get_scheduled_criteria_for_date(
        self, user: User, for_date: datetime
    ) -> Tuple[List[CategoryName], List[str]]:
        """Get categories and channels that should be considered for the given date based on user schedule."""
        target_date = for_date.date()
        scheduled_contents = user.schedule.get_scheduled_content_list_for_date(
            target_date
        )

        allowed_categories = set()
        scheduled_channels = set()

        for content in scheduled_contents:
            allowed_categories.update(content.allowed_categories)
            scheduled_channels.update(content.youtube_channels)

        return list(allowed_categories), list(scheduled_channels)
