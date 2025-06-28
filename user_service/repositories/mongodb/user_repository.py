"""
MongoDB implementation of the UserRepository interface.
"""

from typing import Optional
from uuid import UUID
from pymongo.errors import DuplicateKeyError
from ...models.user import User
from ..user_repository import UserRepository
from .config.settings import get_mongodb_settings
from .config.database import MongoDB
from .adapters.user_adapter import UserAdapter
from .models.user_db_model import UserDBModel

class MongoDBUserRepository(UserRepository):
    """MongoDB implementation of user repository."""
    
    def __init__(self):
        self.settings = get_mongodb_settings()
        if MongoDB.db is None:
            MongoDB.connect_to_database()
        self.collection = MongoDB.get_database()[self.settings.COLLECTION_NAME]
        # Create unique index on email field
        self.collection.create_index("email", unique=True)
    
    def create_user(self, user: User) -> User:
        """Create a new user in MongoDB."""
        db_model = UserAdapter.to_db_model(user)
        try:
            self.collection.insert_one(db_model.model_dump(by_alias=True))
            return user
        except DuplicateKeyError:
            raise Exception("A user with this email already exists.")
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Retrieve a user from MongoDB by their ID."""
        user_dict = await self.collection.find_one({"_id": str(user_id)})
        if user_dict:
            db_model = UserDBModel(**user_dict)
            return UserAdapter.to_internal_model(db_model)
        return None 