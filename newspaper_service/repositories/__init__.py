"""
Repositories package for newspaper service.
"""

from .generated_content_repository import GeneratedContentRepository
from .newspaper_repository import NewspaperRepository
from .user_collected_content_repository import UserCollectedContentRepository

__all__ = [
    "NewspaperRepository",
    "UserCollectedContentRepository",
    "GeneratedContentRepository",
]
