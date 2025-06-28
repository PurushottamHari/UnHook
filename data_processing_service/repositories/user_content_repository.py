"""
Abstract base class for user content repository.
"""

from abc import ABC, abstractmethod
from typing import List
from data_collector_service.models.user_collected_content import UserCollectedContent, ContentStatus, ContentSubStatus, ContentType

class UserContentRepository(ABC):
    """Abstract base class for managing user content data."""
    
    @abstractmethod
    def get_unprocessed_content_for_user(self, user_id: str) -> List[UserCollectedContent]:
        """
        Get list of unprocessed content for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[Dict]: List of unprocessed content items
        """
        pass 

    @abstractmethod
    def update_user_collected_content_batch(self, updated_user_collected_content_list: List[UserCollectedContent]):
        pass

    @abstractmethod
    def get_user_collected_content(
        self, 
        user_id: str, 
        status: ContentStatus, 
        sub_status: ContentSubStatus, 
        content_type: ContentType) -> List[UserCollectedContent]:
        pass