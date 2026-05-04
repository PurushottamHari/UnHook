"""
Service for considering and tracking user collected content article candidates for newspapers.
"""

import logging
import uuid

from injector import inject

from commons.infra.dependency_injection.injectable import injectable

from ...models import (CandidateLinks, CandidateSource, CandidateStatus,
                       CandidateType, NewspaperArticleCandidate)
from ...repositories.newspaper_article_candidate_repository import \
    NewspaperArticleCandidateRepository
from ...repositories.user_collected_content_repository import \
    UserCollectedContentRepository


class ContentNotFoundError(Exception):
    """Raised when source content is not found."""

    pass


@injectable()
class ConsiderUserCollectedContentArticleCandidateService:
    """Service for considering and tracking user collected content article candidates for newspapers."""

    @inject
    def __init__(
        self,
        user_collected_content_repository: UserCollectedContentRepository,
        candidate_repository: NewspaperArticleCandidateRepository,
    ):
        self.user_collected_content_repository = user_collected_content_repository
        self.candidate_repository = candidate_repository
        self.logger = logging.getLogger(__name__)

    async def consider_candidate(
        self,
        user_id: str,
        user_collected_content_id: str,
    ) -> None:
        """
        Consider and track an article candidate for a newspaper.
        """
        # Hardcoded for this specific service
        source = CandidateSource.USER_COLLECTED_CONTENT
        type = CandidateType.USER_COLLECTED_CONTENT

        try:
            # 1. Verify existence of the collected content
            content = self.user_collected_content_repository.get_content_by_id(
                user_collected_content_id
            )
            if not content:
                # Raise alert/exception for fail-fast behavior
                error_msg = f"ALERT: Content {user_collected_content_id} not found for user {user_id}"
                self.logger.error(error_msg)
                raise ContentNotFoundError(error_msg)

            # 2. Get or Create candidate
            linked_id = user_collected_content_id
            candidate = self.candidate_repository.get_candidate_by_linked_id(linked_id)

            if not candidate:
                # Prepare the new candidate object
                candidate = NewspaperArticleCandidate(
                    id=str(uuid.uuid4()),
                    linked_id=linked_id,
                    source=source,
                    type=type,
                    user_id=user_id,
                    links=CandidateLinks(
                        user_collected_content_id=user_collected_content_id
                    ),
                    status=CandidateStatus.CONSIDERED,
                    version=1,
                )
                candidate.set_status(
                    CandidateStatus.CONSIDERED, "Initial creation from request"
                )
                self.logger.info(
                    f"Preparing to create new candidate for linked_id: {linked_id}"
                )
                # 3. Upsert into database
                candidate = self.candidate_repository.upsert_candidate(candidate)
                self.logger.info(
                    f"Successfully upserted candidate for linked_id: {linked_id}"
                )
            else:
                self.logger.info(f"Candidate already exists for linked_id: {linked_id}")

        except Exception as e:
            self.logger.error(
                f"Error in ConsiderUserCollectedContentArticleCandidateService: {str(e)}"
            )
            raise
