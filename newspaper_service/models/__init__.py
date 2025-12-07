"""
Models package for newspaper service.
"""

from .generated_content_interaction import (
    GeneratedContentInteraction, InteractionStatus, InteractionType,
    InteractionTypeDetail)
from .generated_content_interaction_list import \
    GeneratedContentInteractionListResponse
from .generated_content_list import GeneratedContentListResponse
from .newspaper import (ConsideredContent, ConsideredContentStatus,
                        ConsideredContentStatusDetail, Newspaper,
                        NewspaperStatus, StatusDetail)
from .newspaper_list import NewspaperListData, NewspaperListResponse

__all__ = [
    "NewspaperStatus",
    "Newspaper",
    "StatusDetail",
    "ConsideredContent",
    "ConsideredContentStatus",
    "ConsideredContentStatusDetail",
    "GeneratedContentInteraction",
    "InteractionType",
    "InteractionStatus",
    "InteractionTypeDetail",
    "GeneratedContentInteractionListResponse",
    "GeneratedContentListResponse",
    "NewspaperListData",
    "NewspaperListResponse",
]
