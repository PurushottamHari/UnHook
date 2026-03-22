"""
Service for processing moderated content for users.
"""

from data_collector_service.models.user_collected_content import ContentType
from data_processing_service.external.user_service.client import UserServiceClient
from data_processing_service.repositories.mongodb.config.database import MongoDB
from data_processing_service.repositories.mongodb.user_content_repository import (
    MongoDBUserContentRepository,
)
from data_processing_service.services.processing.youtube.process_moderated_content.process_moderated_youtube_content_service import (
    ProcessModeratedYoutubeContentService,
)
from user_service.models.user import User


class ProcessModeratedContentService:
    """Service for processing moderated content for users."""

    def __init__(self):
        self.user_service_client = UserServiceClient()

        # Initialize MongoDB connection if not already connected
        if MongoDB.db is None:
            MongoDB.connect_to_database()

        # Create MongoDB user content repository
        user_content_repository = MongoDBUserContentRepository(MongoDB.get_database())

        # Initialize YouTube content service with the repository
        self.youtube_content_service = ProcessModeratedYoutubeContentService(
            user_content_repository
        )

    def process(self, user_id: str, content_type: ContentType) -> None:
        """
        Process moderated content for a specific user.

        Args:
            user_id: The unique identifier of the user
        """
        # Get user data
        user = self.user_service_client.get_user(user_id)

        if not user:
            raise RuntimeError("User not found: " + user_id)

        # Check if user has manual youtube config
        if content_type == ContentType.YOUTUBE_VIDEO:
            # Process moderated youtube content
            self.youtube_content_service.process(user)
        else:
            raise RuntimeError("Content Type not supported: " + content_type)


if __name__ == "__main__":
    user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"
    service = ProcessModeratedContentService()
    service.process(user_id=user_id, content_type=ContentType.YOUTUBE_VIDEO)
    print(f"Processing for user {user_id} complete.")
