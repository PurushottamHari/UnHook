"""
MongoDB database connection configuration.
"""

from injector import inject
from pymongo import MongoClient

from commons.infra.dependency_injection.injectable import injectable

from .settings import get_mongodb_settings


@injectable()
class MongoDB:
    """MongoDB connection manager."""

    @inject
    def __init__(self):
        pass

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
            client = MongoClient(connection_uri, uuidRepresentation="standard")
            cls._db = client[settings.DATABASE_NAME]
            # Verify connection
            try:
                client.admin.command("ping")
                print("✅ [MongoDB] Connected successfully")
            except Exception as e:
                print(f"❌ [MongoDB] Connection failed: {e}")
        return cls._instance

    @classmethod
    def get_database(cls):
        """Get database instance."""
        if cls._db is None:
            MongoDB()
        return cls._db
