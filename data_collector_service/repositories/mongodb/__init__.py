"""
MongoDB repository implementation package.
"""

from .config.database import MongoDB
from .user_collected_content_repository import \
    MongoDBUserCollectedContentRepository

__all__ = ["MongoDBUserCollectedContentRepository", "MongoDB"]
