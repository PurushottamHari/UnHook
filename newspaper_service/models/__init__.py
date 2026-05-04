"""
Models package for newspaper service.
"""

from .generated_content_interaction import (GeneratedContentInteraction,
                                            InteractionStatus, InteractionType,
                                            InteractionTypeDetail)
from .generated_content_interaction_list import \
    GeneratedContentInteractionListResponse
from .generated_content_list import GeneratedContentListResponse
from .newspaper import (ConsideredContent, ConsideredContentStatus,
                        ConsideredContentStatusDetail, Newspaper,
                        NewspaperStatus, StatusDetail)
from .newspaper_article_candidate import (CandidateLinks, CandidateSource,
                                          CandidateStatus,
                                          CandidateStatusDetail, CandidateType,
                                          NewspaperArticleCandidate)
from .newspaper_list import NewspaperListData, NewspaperListResponse
from .newspaper_v2 import NewspaperV2

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
    "CandidateStatus",
    "CandidateStatusDetail",
    "CandidateLinks",
    "CandidateSource",
    "CandidateType",
    "NewspaperArticleCandidate",
    "NewspaperV2",
]
