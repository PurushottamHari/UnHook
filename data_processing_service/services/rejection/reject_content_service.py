"""
Service for handling content rejection.
"""

from typing import List
from ...external.user_service.client import UserServiceClient
from ...repositories.user_content_repository import UserContentRepository
from ...repositories.mongodb.config.database import MongoDB
from ...repositories.mongodb.user_content_repository import MongoDBUserContentRepository
from data_collector_service.models.enums import ContentType
from .youtube.rejection_content_service_youtube import RejectionContentServiceYoutube
from data_processing_service.services.rejection.youtube.ai_agent.moderator import ContentModerator
import asyncio


class RejectContentService:
    """Service for handling content rejection."""
    
    def __init__(
        self,
        user_service_client: UserServiceClient,
        rejection_content_service_youtube: RejectionContentServiceYoutube,

    ):
        """
        Initialize the service.
        
        Args:
            user_service_client: Client for user service
            user_content_repository: Repository for user content
        """
        self.user_service_client = user_service_client
        # Initialize MongoDB connection
        MongoDB.connect_to_database()
        # Create MongoDB repository instance
        self.user_content_repository = MongoDBUserContentRepository(MongoDB.get_database())
        self.rejection_content_service_youtube = rejection_content_service_youtube
    
    async def reject(self, user_id: str) -> None:
        """
        Reject content for a user.
        
        Args:
            user_id: The ID of the user
        """
        # Get user object from user service
        user = self.user_service_client.get_user(user_id)
        
        # Get unprocessed content for the user
        unprocessed_content_list = self.user_content_repository.get_unprocessed_content_for_user(user_id)

        # Collect unprocessed content in a map by content_type
        content_map = {}
        for unprocessed_content in unprocessed_content_list:
            content_type = unprocessed_content.content_type
            if content_type not in content_map:
                content_map[content_type] = []
            content_map[content_type].append(unprocessed_content)

        # Process each content type
        rejected_content = []
        for content_type, contents in content_map.items():
            if content_type == ContentType.YOUTUBE_VIDEO:
                print(f"Found {len(contents)} elements to process for Youtube")
                moderated_youtube_content = await self.rejection_content_service_youtube.reject(user=user, contents=contents)
                if len(moderated_youtube_content) != len(contents):
                    raise ValueError(f"Mismatch in moderated content count: expected {len(contents)}, got {len(moderated_youtube_content)}")
                rejected_content.extend(moderated_youtube_content)
            else:
                for content in contents:
                    print("Unsupported Content type!: " + content.id + " - " + content_type)

        
        if len(rejected_content) != 0:
            self.user_content_repository.update_user_collected_content_batch(rejected_content)

if __name__ == "__main__":
    user_service_client = UserServiceClient()
    moderator_agent = ContentModerator()
    rejection_content_service_youtube = RejectionContentServiceYoutube(moderator_agent)
    reject_content_service = RejectContentService(
        user_service_client=user_service_client,
        rejection_content_service_youtube=rejection_content_service_youtube
    )
    # Call reject with a custom user_id
    custom_user_id = "607d95f0-47ef-444c-89d2-d05f257d1265"  # Replace with your desired user_id
    asyncio.run(reject_content_service.reject(custom_user_id))
