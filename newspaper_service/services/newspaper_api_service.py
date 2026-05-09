import logging
from datetime import datetime, timezone
from typing import List, Optional

import pytz
from fastapi import HTTPException
from injector import inject

from commons.infra.dependency_injection.injectable import injectable

from ..api.adaptors.newspaper_v2_adaptor import NewspaperV2Adaptor
from ..api.models.newspaper_v2_response import NewspaperV2Response
from ..external.user_service import UserServiceClient
from ..models import CandidateStatus, NewspaperV2
from ..repositories.generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from ..repositories.generated_content_repository import \
    GeneratedContentRepository
from ..repositories.newspaper_article_candidate_repository import \
    NewspaperArticleCandidateRepository
from ..repositories.newspaper_v2_repository import NewspaperV2Repository
from .newspaper_utils import aggregate_newspapers

NEWSPAPER_PAGE_LIMIT = 10


@injectable()
class NewspaperApiService:
    """Service for handling consolidated Newspaper V2 API requests."""

    @inject
    def __init__(
        self,
        newspaper_v2_repository: NewspaperV2Repository,
        candidate_repository: NewspaperArticleCandidateRepository,
        generated_content_repository: GeneratedContentRepository,
        interaction_repository: GeneratedContentInteractionRepository,
        user_service_client: UserServiceClient,
    ):
        self._newspaper_v2_repository = newspaper_v2_repository
        self._candidate_repository = candidate_repository
        self._generated_content_repository = generated_content_repository
        self._interaction_repository = interaction_repository
        self._user_service_client = user_service_client
        self.logger = logging.getLogger(__name__)

    async def get_newspaper_with_articles_v2(
        self,
        user_id: str,
        date_str: str,
        starting_after: Optional[str] = None,
        timezone_str: str = "UTC",
    ) -> NewspaperV2Response:
        """
        Consolidated API to get newspaper metadata and paginated articles by date,
        accounting for timezone-specific boundaries.
        """
        # 1. Validate user
        user = await self._user_service_client.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_id}")

        # 2. Parse date and calculate timezone-aware boundaries
        try:
            base_date = datetime.strptime(date_str, "%d/%m/%Y")
            try:
                tz = pytz.timezone(timezone_str)
            except pytz.UnknownTimeZoneError:
                raise HTTPException(
                    status_code=400, detail=f"Unknown timezone: {timezone_str}"
                )

            # Calculate start and end of day in the specified timezone
            start_of_day = tz.localize(
                base_date.replace(hour=0, minute=0, second=0, microsecond=0)
            )
            end_of_day = tz.localize(
                base_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            )
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Expected DD/MM/YYYY"
            )

        # 3. Fetch all newspapers within this local day range
        newspapers = self._newspaper_v2_repository.list_by_user_and_date_range(
            user_id, start_of_day, end_of_day
        )

        if not newspapers:
            raise HTTPException(
                status_code=404, detail=f"No newspaper found for date: {date_str}"
            )

        # Get all USED candidates for ALL newspapers found in this day
        newspaper_ids = [n.id for n in newspapers]
        candidates = self._candidate_repository.list_candidates_by_newspaper_ids(
            newspaper_ids=newspaper_ids, status=CandidateStatus.USED
        )

        # Aggregate metadata from multiple newspapers
        newspaper = aggregate_newspapers(newspapers, candidates)

        if not candidates:
            return NewspaperV2Adaptor.to_newspaper_v2_response(
                newspaper=newspaper, articles=[], has_next=False
            )

        # Filter and sort candidates by external_id
        valid_candidates = [
            c
            for c in candidates
            if c.links.source_list and c.links.source_list[0].external_id
        ]

        # Sort candidates by external_id (consistent sorting for pagination)
        valid_candidates.sort(key=lambda x: x.links.source_list[0].external_id)

        # Apply Pagination
        start_index = 0
        if starting_after:
            try:
                start_index = (
                    next(
                        i
                        for i, c in enumerate(valid_candidates)
                        if c.links.source_list[0].external_id == starting_after
                    )
                    + 1
                )
            except StopIteration:
                start_index = 0

        paginated_candidates = valid_candidates[
            start_index : start_index + NEWSPAPER_PAGE_LIMIT + 1
        ]
        has_next = len(paginated_candidates) > NEWSPAPER_PAGE_LIMIT
        final_candidates = paginated_candidates[:NEWSPAPER_PAGE_LIMIT]

        next_cursor = (
            final_candidates[-1].links.source_list[0].external_id
            if final_candidates and has_next
            else None
        )

        if not final_candidates:
            return NewspaperV2Adaptor.to_newspaper_v2_response(
                newspaper=newspaper, articles=[], has_next=False
            )

        # 9. Fetch Required GeneratedContent objects
        gen_content_ids = [c.links.generated_content_id for c in final_candidates]
        contents = self._generated_content_repository.get_contents_by_ids(
            gen_content_ids
        )

        # Maintain order of final_candidates
        content_map = {c.id: c for c in contents}
        ordered_contents = [
            content_map[cid] for cid in gen_content_ids if cid in content_map
        ]

        # Fetch Interactions
        content_ids = [c.id for c in ordered_contents]
        interactions_map = self._interaction_repository.get_active_interactions_by_generated_content_ids(
            user_id=user_id, generated_content_ids=content_ids
        )

        # Transform to API models
        candidate_map = {c.links.generated_content_id: c for c in final_candidates}
        article_responses = [
            NewspaperV2Adaptor.to_article_response(
                content=content,
                source_detail=candidate_map[content.id].links.source_list[0],
                interactions=interactions_map.get(content.id, []),
            )
            for content in ordered_contents
            if content.id in candidate_map
            and candidate_map[content.id].links.source_list
        ]

        return NewspaperV2Adaptor.to_newspaper_v2_response(
            newspaper=newspaper,
            articles=article_responses,
            has_next=has_next,
            next_cursor=next_cursor,
        )
