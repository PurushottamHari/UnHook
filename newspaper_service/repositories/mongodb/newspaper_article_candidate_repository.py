"""
MongoDB implementation of NewspaperArticleCandidateRepository.
"""

import logging
from typing import List, Optional

from injector import inject

from commons.infra.dependency_injection.injectable import injectable

from ...models import CandidateStatus, NewspaperArticleCandidate
from ..newspaper_article_candidate_repository import \
    NewspaperArticleCandidateRepository
from .adapters.newspaper_article_candidate_adapter import \
    NewspaperArticleCandidateAdapter
from .config.database import MongoDB
from .config.settings import get_mongodb_settings
from .models.newspaper_article_candidate_db_model import \
    NewspaperArticleCandidateDBModel
from .utils.optimistic_locking import create_optimistic_locking_update_op


@injectable()
class MongoDBNewspaperArticleCandidateRepository(NewspaperArticleCandidateRepository):
    """MongoDB implementation of newspaper article candidate repository."""

    @inject
    def __init__(self, mongodb: MongoDB):
        self.settings = get_mongodb_settings()
        self.collection = mongodb.get_database()[
            self.settings.NEWSPAPER_ARTICLE_CANDIDATE_COLLECTION_NAME
        ]
        self.logger = logging.getLogger(__name__)
        # Ensure unique index on linked_id for idempotency
        self.collection.create_index("linked_id", unique=True)

    def upsert_candidate(
        self, candidate: NewspaperArticleCandidate
    ) -> NewspaperArticleCandidate:
        """Upsert a single candidate with optimistic locking."""
        try:
            results = self.upsert_candidates([candidate])
            return results[0]
        except Exception as e:
            self.logger.error(f"Error upserting candidate: {str(e)}")
            raise

    def upsert_candidates(
        self, candidates: List[NewspaperArticleCandidate]
    ) -> List[NewspaperArticleCandidate]:
        """Bulk upsert candidates with optimistic locking."""
        if not candidates:
            return []

        try:
            ops = []
            for candidate in candidates:
                db_model = NewspaperArticleCandidateAdapter.to_db_model(candidate)
                update_dict = db_model.model_dump(by_alias=True, exclude={"id"})

                # We use linked_id as the business key for upserting
                op = create_optimistic_locking_update_op(
                    filter_query={"linked_id": candidate.linked_id},
                    update_dict=update_dict,
                    version=candidate.version,
                    id_for_insert=candidate.id,
                )
                ops.append(op)

            if ops:
                result = self.collection.bulk_write(ops)
                self.logger.info(
                    f"✅ [CandidateRepository] Upserted {len(candidates)} items (Matched: {result.matched_count}, Upserted: {result.upserted_count})"
                )

            return candidates
        except Exception as e:
            self.logger.error(f"Error bulk upserting candidates: {str(e)}")
            raise

    def get_candidate_by_id(
        self, candidate_id: str
    ) -> Optional[NewspaperArticleCandidate]:
        """Get a single candidate by ID."""
        doc = self.collection.find_one({"_id": candidate_id})
        if doc:
            db_model = NewspaperArticleCandidateDBModel(**doc)
            return NewspaperArticleCandidateAdapter.to_internal_model(db_model)
        return None

    def get_candidate_by_linked_id(
        self, linked_id: str
    ) -> Optional[NewspaperArticleCandidate]:
        """Get a single candidate by linked ID (business key)."""
        doc = self.collection.find_one({"linked_id": linked_id})
        if doc:
            db_model = NewspaperArticleCandidateDBModel(**doc)
            return NewspaperArticleCandidateAdapter.to_internal_model(db_model)
        return None

    def list_candidates_by_user_and_status(
        self, user_id: str, status: CandidateStatus
    ) -> List[NewspaperArticleCandidate]:
        """List candidates for a user with a specific status."""
        cursor = self.collection.find({"user_id": user_id, "status": status.value})
        candidates = []
        for doc in cursor:
            db_model = NewspaperArticleCandidateDBModel(**doc)
            candidates.append(
                NewspaperArticleCandidateAdapter.to_internal_model(db_model)
            )
        return candidates
