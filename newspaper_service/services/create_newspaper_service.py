"""
Main newspaper service for orchestrating newspaper creation.
"""

import asyncio
import copy
import logging
from datetime import datetime
from typing import List
from uuid import uuid4

import pytz

from data_collector_service.models.user_collected_content import (
    ContentStatus, UserCollectedContent)

from ..external.user_service import UserServiceClient
from ..models import (ConsideredContent, ConsideredContentStatus, Newspaper,
                      NewspaperStatus)
from ..repositories import NewspaperRepository, UserCollectedContentRepository
from ..repositories.mongodb.config.database import MongoDB
from ..repositories.mongodb.newspaper_repository import \
    MongoDBNewspaperRepository
from ..repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository


class CreateNewspaperService:
    """Main service for newspaper creation and management."""

    def __init__(
        self,
        newspaper_repository: NewspaperRepository,
        user_collected_content_repository: UserCollectedContentRepository,
    ):
        self.newspaper_repository = newspaper_repository
        self.user_collected_content_repository = user_collected_content_repository
        self.logger = logging.getLogger(__name__)
        self.user_service_client = UserServiceClient()

    async def create_newspaper_for_user(
        self, user_id: str, for_date: datetime
    ) -> Newspaper:
        """Create a newspaper for a specific user for the given date.

        Flow:
        - Fetch user_collected_content in PROCESSED status on or before for_date
        - Create Newspaper in COLLATING with considered_content_list populated
        - Update those user_collected_content items to PICKED_FOR_EVALUATION
        - Single DB call to create the newspaper and update content statuses
        """
        try:
            self.logger.info(f"Creating newspaper for user {user_id} for {for_date}")

            # Fetch user to determine allowed reading time
            user = self.user_service_client.get_user(user_id)
            if not user:
                raise RuntimeError(f"User not found: {user_id}")
            reading_time_seconds: int = user.max_reading_time_per_day_mins * 60

            # Fetch processed collected content ids on or before date
            processed_content_list = (
                self.user_collected_content_repository.get_content_with_status(
                    user_id=user_id,
                    status=ContentStatus.PROCESSED,
                    before_time=for_date,
                )
            )

            self.logger.info(f"Found {len(processed_content_list)} processed contents")
            processed_ids: List[str] = [c.id for c in processed_content_list]

            # Build considered_content_list
            considered_items: List[ConsideredContent] = []
            updated_content_list: List[UserCollectedContent] = []
            for processed_content in processed_content_list:
                item = ConsideredContent(
                    user_collected_content_id=processed_content.id,
                    considered_content_status=ConsideredContentStatus.PENDING,
                )
                # initialize status history
                item.set_status(
                    ConsideredContentStatus.PENDING,
                    reason="Picked for evaluation consideration",
                )
                considered_items.append(item)
                updated_user_collected_content = copy.deepcopy(processed_content)
                updated_user_collected_content.set_status(
                    ContentStatus.PICKED_FOR_EVALUATION
                )
                updated_content_list.append(updated_user_collected_content)

            # Create Newspaper and set COLLATING
            newspaper = Newspaper(
                id=str(uuid4()),
                user_id=user_id,
                status=NewspaperStatus.COLLATING,
                reading_time_in_seconds=reading_time_seconds,
            )
            newspaper.set_status(NewspaperStatus.COLLATING, "Starting collation")
            newspaper.considered_content_list = considered_items

            # Single DB call: create newspaper and mark content as PICKED_FOR_EVALUATION
            created_newspaper = self.newspaper_repository.create_newspaper(
                newspaper, updated_content_list
            )

            self.logger.info(
                f"Successfully created newspaper {created_newspaper.id} with {len(processed_ids)} considered items"
            )
            return created_newspaper

        except Exception as e:
            self.logger.error(f"Error creating newspaper for user {user_id}: {str(e)}")
            raise


async def main():
    # Set up logger
    logging.basicConfig(level=logging.INFO)

    # Initialize repositories
    user_collected_content_repository = MongoDBUserCollectedContentRepository()
    newspaper_repository = MongoDBNewspaperRepository(
        user_collected_content_repository=user_collected_content_repository
    )

    # Initialize service
    service = CreateNewspaperService(
        newspaper_repository=newspaper_repository,
        user_collected_content_repository=user_collected_content_repository,
    )

    # Example usage: replace with actual user_id
    user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"

    # Accept date in "dd/mm/yyyy" format from user input
    # date_str = "01/01/2024"
    # ist = pytz.timezone("Asia/Kolkata")
    # day, month, year = map(int, date_str.strip().split("/"))
    # naive_dt = datetime(year, month, day, 11, 59)
    # for_date = ist.localize(naive_dt)

    # Calculate for_date from hardcoded epoch 1752911100
    epoch = 1752911100
    for_date = datetime.fromtimestamp(epoch, pytz.timezone("Asia/Kolkata"))

    newspaper = await service.create_newspaper_for_user(user_id, for_date)
    print(f"Created newspaper: {newspaper.id}")


if __name__ == "__main__":
    asyncio.run(main())
