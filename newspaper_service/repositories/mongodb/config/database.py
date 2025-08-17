"""
MongoDB database connection configuration.
"""

from pymongo import MongoClient

from .settings import get_mongodb_settings


class MongoDB:
    """MongoDB connection manager."""

    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            settings = get_mongodb_settings()
            # Prefer MONGODB_URI, fallback to MONGODB_URL for compatibility
            connection_uri = settings.MONGODB_URI or settings.MONGODB_URL
            if not connection_uri:
                raise RuntimeError(
                    "MongoDB connection string not configured. Set MONGODB_URI or MONGODB_URL."
                )
            client = MongoClient(connection_uri)
            cls._db = client[settings.DATABASE_NAME]
        return cls._instance

    @classmethod
    def get_database(cls):
        """Get database instance."""
        if cls._db is None:
            MongoDB()
        return cls._db
