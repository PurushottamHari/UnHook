"""
Repositories package for newspaper service.
"""

from .generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from .generated_content_repository import GeneratedContentRepository
from .newspaper_article_candidate_repository import \
    NewspaperArticleCandidateRepository
from .newspaper_repository import NewspaperRepository
from .newspaper_v2_repository import NewspaperV2Repository
from .user_collected_content_repository import UserCollectedContentRepository

__all__ = [
    "NewspaperRepository",
    "NewspaperV2Repository",
    "NewspaperArticleCandidateRepository",
    "UserCollectedContentRepository",
    "GeneratedContentRepository",
    "GeneratedContentInteractionRepository",
]
