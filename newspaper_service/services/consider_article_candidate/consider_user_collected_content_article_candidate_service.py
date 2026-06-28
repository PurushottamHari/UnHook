"""
Service for considering and tracking user collected content article candidates for newspapers.
"""

import logging
import uuid

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.enums import ContentType
from injector import inject

from ...models import (
    CandidateLinks,
    CandidateSource,
    CandidateSourceDetail,
    CandidateStatus,
    CandidateType,
    NewspaperArticleCandidate,
    SourceType,
)
from ...repositories.generated_content_repository import GeneratedContentRepository
from ...repositories.newspaper_article_candidate_repository import (
    NewspaperArticleCandidateRepository,
)
from ...repositories.user_collected_content_repository import (
    UserCollectedContentRepository,
)
from ...repositories.youtube_collected_content_repository import (
    YouTubeCollectedContentRepository,
)


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
        youtube_repository: YouTubeCollectedContentRepository,
        generated_content_repository: GeneratedContentRepository,
    ):
        self.user_collected_content_repository = user_collected_content_repository
        self.candidate_repository = candidate_repository
        self.youtube_repository = youtube_repository
        self.generated_content_repository = generated_content_repository
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
                # 3. Handle source-specific metadata fetching
                metadata = {}
                source_type = None
                generated_content_id = None

                if content.content_type == ContentType.YOUTUBE_VIDEO:
                    source_type = SourceType.YOUTUBE_VIDEO
                    try:
                        youtube_details = self.youtube_repository.get_video_by_id(
                            content.external_id
                        )
                        metadata = {
                            "youtube_video_link": f"https://www.youtube.com/watch?v={content.external_id}"
                        }
                        if youtube_details:
                            metadata["channel_name"] = youtube_details.channel_name
                        else:
                            metadata["channel_name"] = ""
                    except Exception as e:
                        self.logger.warning(
                            f"Could not fetch YouTube details for {content.external_id}: {e}"
                        )
                        raise ValueError(
                            f"Could not fetch YouTube details for {content.external_id}: {e}"
                        )

                # 4. Find linked generated content if it exists
                try:
                    gen_content = (
                        self.generated_content_repository.get_content_by_external_id(
                            content.external_id
                        )
                    )
                    if gen_content:
                        generated_content_id = gen_content.id
                except Exception as e:
                    self.logger.warning(
                        f"Could not fetch generated content for {content.external_id}: {e}"
                    )

                # Prepare the new candidate object
                candidate = NewspaperArticleCandidate(
                    id=str(uuid.uuid4()),
                    linked_id=linked_id,
                    source=source,
                    type=type,
                    user_id=user_id,
                    links=CandidateLinks(
                        user_collected_content_id=user_collected_content_id,
                        generated_content_id=generated_content_id,
                        generated_content_id_list=(
                            [generated_content_id] if generated_content_id else []
                        ),
                        source_list=[
                            CandidateSourceDetail(
                                external_id=content.external_id,
                                source_type=source_type,
                                metadata=metadata,
                            )
                        ],
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
