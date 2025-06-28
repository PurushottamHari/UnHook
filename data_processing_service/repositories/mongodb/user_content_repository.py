"""
MongoDB implementation of user content repository.
"""

from typing import List
from data_collector_service.models.user_collected_content import UserCollectedContent, ContentStatus, ContentType, ContentSubStatus
from ..user_content_repository import UserContentRepository
from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import CollectedContentAdapter
from pymongo import UpdateOne
from data_collector_service.repositories.mongodb.models.collected_content_db_model import CollectedContentDBModel

class MongoDBUserContentRepository(UserContentRepository):
    """MongoDB implementation of user content repository."""
    
    def __init__(self, database):
        """
        Initialize the repository.
        
        Args:
            database: MongoDB database instance
        """
        self.database = database
        self.collection = database.collected_content
    
    def get_unprocessed_content_for_user(self, user_id: str) -> List[UserCollectedContent]:
        """
        Get list of unprocessed content for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[UserCollectedContent]: List of unprocessed content items
        """
        cursor = self.collection.find({
            "user_id": str(user_id),
            "status": ContentStatus.COLLECTED
        })
        
        return [CollectedContentAdapter.to_user_collected_content(CollectedContentDBModel(**doc)) for doc in cursor]

    def update_user_collected_content_batch(self, updated_user_collected_content_list: List[UserCollectedContent]):
        """
        Update a batch of UserCollectedContent items in MongoDB.
        Args:
            updated_user_collected_content_list: List of UserCollectedContent objects to update
        """
        operations = []
        for content in updated_user_collected_content_list:
            db_model = CollectedContentAdapter.to_collected_content_db_model(content)
            update_dict = db_model.dict(by_alias=True, exclude_unset=True)
            # Mongodb does not allow _id to be passed even if same
            _id = update_dict.pop('_id')
            operations.append(
                UpdateOne({'_id': _id}, {'$set': update_dict})
            )
        if operations:
            self.collection.bulk_write(operations) 

    def get_user_collected_content(
        self, 
        user_id: str, 
        status: ContentStatus, 
        sub_status: ContentSubStatus, 
        content_type: ContentType) -> List[UserCollectedContent]:
        """
        Get list of content for a user based on the filters
            user_id: The ID of the user
            
        Returns:
            List[UserCollectedContent]: List of content items in processing status with moderation passed
        """
        cursor = self.collection.find({
            "user_id": str(user_id),
            "status": status,
            "sub_status": sub_status,
            "content_type": content_type
        })
        
        return [CollectedContentAdapter.to_user_collected_content(CollectedContentDBModel(**doc)) for doc in cursor] 