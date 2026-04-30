"""
Newspaper article candidate adapter for converting between domain and database models.
"""

from datetime import datetime, timezone
from typing import Optional

from ....models import (CandidateLinks, CandidateSource, CandidateStatus,
                        CandidateStatusDetail, CandidateType,
                        NewspaperArticleCandidate)
from ..models.newspaper_article_candidate_db_model import (
    CandidateLinksDBModel, CandidateStatusDetailDBModel,
    NewspaperArticleCandidateDBModel)


class NewspaperArticleCandidateAdapter:
    """Adapter for converting between newspaper article candidate domain and database models."""

    @staticmethod
    def to_db_model(
        candidate: NewspaperArticleCandidate,
    ) -> NewspaperArticleCandidateDBModel:
        return NewspaperArticleCandidateDBModel(
            id=str(candidate.id),
            linked_id=candidate.linked_id,
            source=candidate.source.value,
            type=candidate.type.value,
            user_id=candidate.user_id,
            links=CandidateLinksDBModel(
                user_collected_content_id=candidate.links.user_collected_content_id,
                generated_content_id=candidate.links.generated_content_id,
                generated_content_id_list=list(
                    candidate.links.generated_content_id_list
                ),
            ),
            newspaper_id=candidate.newspaper_id,
            status=candidate.status.value,
            status_details=[
                NewspaperArticleCandidateAdapter._status_detail_to_db_model(detail)
                for detail in candidate.status_details
            ],
            version=candidate.version,
            created_at=NewspaperArticleCandidateAdapter._datetime_to_float(
                candidate.created_at
            ),
            updated_at=NewspaperArticleCandidateAdapter._datetime_to_float(
                candidate.updated_at
            ),
        )

    @staticmethod
    def to_internal_model(
        db_model: NewspaperArticleCandidateDBModel,
    ) -> NewspaperArticleCandidate:
        return NewspaperArticleCandidate(
            id=db_model.id,
            linked_id=db_model.linked_id,
            source=CandidateSource(db_model.source),
            type=CandidateType(db_model.type),
            user_id=db_model.user_id,
            links=CandidateLinks(
                user_collected_content_id=db_model.links.user_collected_content_id,
                generated_content_id=db_model.links.generated_content_id,
                generated_content_id_list=list(
                    db_model.links.generated_content_id_list
                ),
            ),
            newspaper_id=db_model.newspaper_id,
            status=CandidateStatus(db_model.status),
            status_details=[
                NewspaperArticleCandidateAdapter._status_detail_to_internal_model(
                    detail
                )
                for detail in db_model.status_details
            ],
            version=db_model.version,
            created_at=NewspaperArticleCandidateAdapter._float_to_datetime(
                db_model.created_at
            ),
            updated_at=NewspaperArticleCandidateAdapter._float_to_datetime(
                db_model.updated_at
            ),
        )

    @staticmethod
    def _status_detail_to_db_model(
        detail: CandidateStatusDetail,
    ) -> CandidateStatusDetailDBModel:
        return CandidateStatusDetailDBModel(
            status=detail.status.value,
            created_at=NewspaperArticleCandidateAdapter._datetime_to_float(
                detail.created_at
            ),
            reason=detail.reason,
        )

    @staticmethod
    def _status_detail_to_internal_model(
        db_detail: CandidateStatusDetailDBModel,
    ) -> CandidateStatusDetail:
        return CandidateStatusDetail(
            status=CandidateStatus(db_detail.status),
            created_at=NewspaperArticleCandidateAdapter._float_to_datetime(
                db_detail.created_at
            ),
            reason=db_detail.reason,
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
