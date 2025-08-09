"""
Repositories package for newspaper service.
"""

from .newspaper_repository import NewspaperRepository
from .user_collected_content_repository import UserCollectedContentRepository

__all__ = [
    "NewspaperRepository",
    "UserCollectedContentRepository",
]
