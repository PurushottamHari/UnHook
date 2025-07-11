"""
MongoDB database connection manager.
"""

from motor.motor_asyncio import AsyncIOMotorClient

from .settings import get_mongodb_settings


class MongoDB:
    """MongoDB connection manager."""

    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        """Create database connection."""
        settings = get_mongodb_settings()
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        cls.db = cls.client[settings.DATABASE_NAME]

    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None

    @classmethod
    def get_database(cls):
        """Get database instance."""
        return cls.db
