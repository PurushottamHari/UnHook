"""
MongoDB repositories package for newspaper service.
"""

from .generated_content_interaction_repository import \
    MongoDBGeneratedContentInteractionRepository

__all__ = [
    "MongoDBGeneratedContentInteractionRepository",
]
