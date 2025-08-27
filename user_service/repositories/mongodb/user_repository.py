"""
MongoDB implementation of the UserRepository interface.
"""

from typing import Optional
from uuid import UUID

from pymongo.errors import DuplicateKeyError

from models.user import User
from repositories.user_repository import UserRepository

from .adapters.user_adapter import UserAdapter
from .config.database import MongoDB
from .config.settings import get_mongodb_settings
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

    async def update_user(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update a user in MongoDB by their ID."""
        # Only allow updating specific fields
        allowed_fields = {
            "max_reading_time_per_day_mins",
            "interested",
            "not_interested",
            "manual_configs",
        }

        # Filter out non-editable fields
        filtered_data = {k: v for k, v in user_data.items() if k in allowed_fields}

        if not filtered_data:
            raise Exception("No valid fields to update")

        # Convert to DB model format
        db_data = {}
        for key, value in filtered_data.items():
            if key == "interested" or key == "not_interested":
                db_data[key] = [
                    item.model_dump() if hasattr(item, "model_dump") else item
                    for item in value
                ]
            elif key == "manual_configs":
                db_data[key] = (
                    value.model_dump() if hasattr(value, "model_dump") else value
                )
            else:
                db_data[key] = value

        result = await self.collection.update_one(
            {"_id": str(user_id)}, {"$set": db_data}
        )

        if result.modified_count > 0:
            return await self.get_user(user_id)
        return None
