"""
Main newspaper service for orchestrating newspaper creation.
"""

import asyncio
import copy
import logging
from datetime import datetime, timedelta
from typing import List, Tuple
from uuid import uuid4

import pytz

from data_collector_service.models.user_collected_content import (
    ContentStatus, UserCollectedContent)
from newspaper_service.external.user_service import UserServiceClient
from newspaper_service.models import (ConsideredContent,
                                      ConsideredContentStatus, Newspaper,
                                      NewspaperStatus)
from newspaper_service.repositories import (GeneratedContentRepository,
                                            NewspaperRepository,
                                            UserCollectedContentRepository)
from newspaper_service.repositories.mongodb.generated_content_repository import \
    MongoDBGeneratedContentRepository
from newspaper_service.repositories.mongodb.newspaper_repository import \
    MongoDBNewspaperRepository
from newspaper_service.repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from user_service.models.enums import CategoryName, Weekday


class CreateNewspaperService:
    """Main service for newspaper creation and management."""

    def __init__(
        self,
        newspaper_repository: NewspaperRepository,
        user_collected_content_repository: UserCollectedContentRepository,
        generated_content_repository: GeneratedContentRepository,
    ):
        self.newspaper_repository = newspaper_repository
        self.user_collected_content_repository = user_collected_content_repository
        self.generated_content_repository = generated_content_repository
        self.logger = logging.getLogger(__name__)
        self.user_service_client = UserServiceClient()

    async def create_newspaper_for_user(
        self, user_id: str, for_date: datetime
    ) -> Newspaper:
        """Create or update a newspaper for a specific user for the given date.

        Flow:
        1. Fetch existing newspaper or create new one with standard template
        2. Get candidates that need to be considered (not already in newspaper)
        3. Add new candidates to newspaper
        4. Update statuses for new candidates
        5. Upsert newspaper and update user collected content
        """
        try:
            self.logger.info(f"Processing newspaper for user {user_id} for {for_date}")

            # Step 1: Fetch existing newspaper or create new one
            newspaper = self._get_or_create_newspaper(user_id, for_date)

            # Step 2: Get candidates that need to be considered
            new_candidates = self._get_new_candidates(user_id, for_date, newspaper)

            if not new_candidates:
                self.logger.info(
                    f"No new candidates to add to newspaper {newspaper.id}"
                )
                return newspaper

            # Step 3: Add new candidates to newspaper
            considered_items, updated_user_contents = self._prepare_candidates(
                new_candidates
            )

            # Step 4: Update newspaper with new candidates
            for item in considered_items:
                newspaper.add_considered_content(item)

            # Step 5: Upsert newspaper
            # Update user content statuses
            self.newspaper_repository.upsert_newspaper(newspaper)
            if updated_user_contents:
                self.user_collected_content_repository.bulk_update_user_collected_content(
                    updated_user_contents
                )

            # Step 6: Mark candidates as ACCEPTED and USED
            # this is being done till a more fleshed out approach comes up
            await self._mark_content_as_accepted_and_used(
                newspaper, considered_items, updated_user_contents
            )

            self.logger.info(
                f"Successfully updated newspaper {newspaper.id} with {len(considered_items)} new items"
            )
            return newspaper

        except Exception as e:
            self.logger.error(
                f"Error processing newspaper for user {user_id}: {str(e)}"
            )
            raise

    def _get_weekday_from_date(self, date: datetime) -> Weekday:
        """Get the weekday enum from a datetime object."""
        weekday_map = {
            0: Weekday.MONDAY,
            1: Weekday.TUESDAY,
            2: Weekday.WEDNESDAY,
            3: Weekday.THURSDAY,
            4: Weekday.FRIDAY,
            5: Weekday.SATURDAY,
            6: Weekday.SUNDAY,
        }
        # Convert to local timezone if needed and get weekday (0=Monday, 6=Sunday)
        local_date = date.astimezone(pytz.timezone("Asia/Kolkata"))
        weekday_num = local_date.weekday()
        return weekday_map[weekday_num]

    def _get_allowed_categories_for_date(
        self, user, for_date: datetime
    ) -> List[CategoryName]:
        """Get categories that should be considered for the given date based on user interests and weekdays."""
        weekday = self._get_weekday_from_date(for_date)
        allowed_categories = []

        for interest in user.interested:
            if weekday in interest.weekdays:
                allowed_categories.append(interest.category_name)

        self.logger.info(f"Allowed categories for {weekday.value} on {for_date}")
        self.logger.info([cat.value for cat in allowed_categories])
        return allowed_categories

    def _get_or_create_newspaper(self, user_id: str, for_date: datetime) -> Newspaper:
        """Fetch existing newspaper or create new one with standard template."""
        # Check if newspaper already exists for the given date
        existing_newspaper = self.newspaper_repository.get_newspaper_by_user_and_date(
            user_id, for_date
        )

        if existing_newspaper:
            self.logger.info(
                f"Found existing newspaper {existing_newspaper.id} for {for_date}"
            )
            return existing_newspaper

        # Create new newspaper with standard template
        self.logger.info(f"Creating new newspaper for {for_date}")
        newspaper = Newspaper(
            id=str(uuid4()),
            user_id=user_id,
            status=NewspaperStatus.COLLATING,
            reading_time_in_seconds=0,  # Will be calculated later
        )
        newspaper.set_status(NewspaperStatus.COLLATING, "Starting collation")
        return newspaper

    def _get_new_candidates(
        self, user_id: str, for_date: datetime, newspaper: Newspaper
    ) -> List[UserCollectedContent]:
        """Get candidates that need to be considered (not already in newspaper)."""
        # Fetch user to determine interests
        user = self.user_service_client.get_user(user_id)
        if not user:
            raise RuntimeError(f"User not found: {user_id}")

        # Get allowed categories for the given date
        allowed_categories = self._get_allowed_categories_for_date(user, for_date)

        # Fetch processed collected content
        processed_content_list = (
            self.user_collected_content_repository.get_content_with_status(
                user_id=user_id,
                status=ContentStatus.PROCESSED,
                before_time=for_date,
            )
        )

        if not processed_content_list:
            return []

        # Filter by categories
        external_ids = [content.external_id for content in processed_content_list]
        filtered_external_ids = (
            self.generated_content_repository.filter_external_ids_by_category(
                external_ids=external_ids,
                categories=allowed_categories,
            )
        )

        # Filter content by external IDs
        filtered_content_list = [
            content
            for content in processed_content_list
            if content.external_id in filtered_external_ids
        ]

        # Filter out content already in newspaper
        existing_content_ids = {
            item.user_collected_content_id for item in newspaper.considered_content_list
        }

        new_candidates = [
            content
            for content in filtered_content_list
            if content.id not in existing_content_ids
        ]

        self.logger.info(
            f"Found {len(new_candidates)} new candidates out of {len(filtered_content_list)} total candidates"
        )
        return new_candidates

    def _prepare_candidates(
        self, candidates: List[UserCollectedContent]
    ) -> Tuple[List[ConsideredContent], List[UserCollectedContent]]:
        """Prepare candidates for newspaper inclusion."""
        considered_items = []
        updated_user_contents = []

        for candidate in candidates:
            # Create considered content item
            item = ConsideredContent(
                user_collected_content_id=candidate.id,
                considered_content_status=ConsideredContentStatus.PENDING,
            )
            item.set_status(
                ConsideredContentStatus.PENDING,
                reason="Picked for evaluation consideration",
            )
            considered_items.append(item)

            # Update user collected content status
            updated_content = copy.deepcopy(candidate)
            updated_content.set_status(ContentStatus.PICKED_FOR_EVALUATION)
            updated_user_contents.append(updated_content)

        return considered_items, updated_user_contents

    async def _mark_content_as_accepted_and_used(
        self,
        newspaper: Newspaper,
        considered_items: List[ConsideredContent],
        updated_user_contents: List[UserCollectedContent],
    ) -> None:
        """Mark considered content as ACCEPTED and user collected content as USED."""
        try:
            # Step 1: Mark considered items as ACCEPTED if not already
            updated_considered_items = []
            for considered_item in considered_items:
                if (
                    considered_item.considered_content_status
                    == ConsideredContentStatus.PENDING
                ):
                    considered_item.set_status(
                        ConsideredContentStatus.ACCEPTED,
                        reason="Content accepted for newspaper",
                    )
                    updated_considered_items.append(considered_item)
                elif (
                    considered_item.considered_content_status
                    == ConsideredContentStatus.ACCEPTED
                ):
                    pass  # Already accepted, do nothing
                else:
                    raise ValueError(
                        f"Cannot mark considered content {considered_item.user_collected_content_id} as ACCEPTED from status {considered_item.considered_content_status}"
                    )

            # Step 2: Mark user collected content as USED if not already
            final_user_contents = []
            for user_content in updated_user_contents:
                if user_content.status in [ContentStatus.PICKED_FOR_EVALUATION]:
                    user_content.set_status(
                        ContentStatus.USED, reason="Content used in newspaper"
                    )
                    final_user_contents.append(user_content)
                elif user_content.status == ContentStatus.USED:
                    # Already used, ignore
                    pass
                else:
                    raise ValueError(
                        f"Cannot mark user_collected_content {user_content.id} as USED from status {user_content.status}"
                    )

            # Step 3: Calculate reading time from all considered content
            all_considered_external_ids = []
            for considered_item in newspaper.considered_content_list:
                user_content = self.user_collected_content_repository.get_content_by_id(
                    considered_item.user_collected_content_id
                )
                if user_content:
                    all_considered_external_ids.append(user_content.external_id)

            reading_times = (
                self.generated_content_repository.get_reading_times_by_external_ids(
                    all_considered_external_ids
                )
            )
            total_reading_time = sum(reading_times.values())
            newspaper.reading_time_in_seconds = total_reading_time

            # Step 4: Update newspaper with new considered items
            for updated_item in updated_considered_items:
                for i, item in enumerate(newspaper.considered_content_list):
                    if (
                        item.user_collected_content_id
                        == updated_item.user_collected_content_id
                    ):
                        newspaper.considered_content_list[i] = updated_item
                        break

            # Step 5: Make repository calls
            self.newspaper_repository.upsert_newspaper(newspaper)
            if final_user_contents:
                self.user_collected_content_repository.bulk_update_user_collected_content(
                    final_user_contents
                )

            self.logger.info(
                f"Marked {len(updated_considered_items)} items as ACCEPTED and {len(final_user_contents)} as USED"
            )

        except Exception as e:
            self.logger.error(f"Error marking content as accepted and used: {str(e)}")
            raise


async def main():
    # Set up logger
    logging.basicConfig(level=logging.INFO)

    # Initialize repositories
    user_collected_content_repository = MongoDBUserCollectedContentRepository()
    generated_content_repository = MongoDBGeneratedContentRepository()
    newspaper_repository = MongoDBNewspaperRepository(
        user_collected_content_repository=user_collected_content_repository
    )

    # Initialize service
    service = CreateNewspaperService(
        newspaper_repository=newspaper_repository,
        user_collected_content_repository=user_collected_content_repository,
        generated_content_repository=generated_content_repository,
    )

    # Example usage: replace with actual user_id
    user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"

    # Use today's date as per the environment where this script is run
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    await service.create_newspaper_for_user(user_id=user_id, for_date=today)


if __name__ == "__main__":
    asyncio.run(main())
