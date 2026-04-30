"""
Repository interface for accessing newspaper_article_candidate collection.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import CandidateStatus, NewspaperArticleCandidate


class NewspaperArticleCandidateRepository(ABC):
    @abstractmethod
    def upsert_candidate(
        self, candidate: NewspaperArticleCandidate
    ) -> NewspaperArticleCandidate:
        """Upsert a single candidate with optimistic locking."""
        pass

    @abstractmethod
    def upsert_candidates(
        self, candidates: List[NewspaperArticleCandidate]
    ) -> List[NewspaperArticleCandidate]:
        """Bulk upsert candidates with optimistic locking."""
        pass

    @abstractmethod
    def get_candidate_by_id(
        self, candidate_id: str
    ) -> Optional[NewspaperArticleCandidate]:
        """Get a single candidate by ID."""
        pass

    @abstractmethod
    def get_candidate_by_linked_id(
        self, linked_id: str
    ) -> Optional[NewspaperArticleCandidate]:
        """Get a single candidate by linked ID (business key)."""
        pass

    @abstractmethod
    def list_candidates_by_user_and_status(
        self, user_id: str, status: CandidateStatus
    ) -> List[NewspaperArticleCandidate]:
        """List candidates for a user with a specific status."""
        pass
