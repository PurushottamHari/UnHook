from datetime import datetime
from typing import Dict, List, Optional

from data_collector_service.models.youtube.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_processing_service.models.generated_content import GeneratedContent

from ...models import CandidateSourceDetail, GeneratedContentInteraction
from ...models.newspaper_v2 import NewspaperV2
from ..models.article_response import (
    ArticleResponse,
    ArticleV2ListResponse,
    CategoryInfo,
    GeneratedData,
    SourceDetails,
    StatusDetail,
)
from ..models.newspaper_v2_response import NewspaperV2Response


class NewspaperV2Adaptor:
    @staticmethod
    def to_status_detail(internal_detail) -> StatusDetail:
        return StatusDetail(
            status=internal_detail.status.value,
            created_at=internal_detail.created_at.timestamp(),
            reason=internal_detail.reason,
        )

    @staticmethod
    def to_generated_data(internal_data) -> GeneratedData:
        return GeneratedData(
            markdown_string=internal_data.markdown_string, string=internal_data.string
        )

    @staticmethod
    def to_category_info(internal_category) -> CategoryInfo:
        if not internal_category:
            return None
        return CategoryInfo(
            category=internal_category.category.value,
            category_description=internal_category.category_description,
            category_tags=internal_category.category_tags,
            shelf_life=(
                internal_category.shelf_life.value
                if internal_category.shelf_life
                else None
            ),
            geography=internal_category.geography,
        )

    @staticmethod
    def to_source_details(
        source_detail: CandidateSourceDetail, content: GeneratedContent
    ) -> SourceDetails:
        if not source_detail:
            # Fallback to content level info if source_detail is missing
            return SourceDetails(
                type=(
                    content.content_type.value
                    if hasattr(content.content_type, "value")
                    else str(content.content_type)
                ),
                external_id=content.external_id,
                metadata={},
            )

        return SourceDetails(
            type=(
                source_detail.source_type.value
                if hasattr(source_detail.source_type, "value")
                else str(source_detail.source_type)
            ),
            external_id=source_detail.external_id,
            metadata=dict(source_detail.metadata),
        )

    @staticmethod
    def to_source_details_from_youtube(
        content: GeneratedContent,
        youtube_details: Optional[YouTubeVideoDetails] = None,
    ) -> SourceDetails:
        if not youtube_details:
            return SourceDetails(
                type=(
                    content.content_type.value
                    if hasattr(content.content_type, "value")
                    else str(content.content_type)
                ),
                external_id=content.external_id,
                metadata={},
            )

        return SourceDetails(
            type=(
                content.content_type.value
                if hasattr(content.content_type, "value")
                else str(content.content_type)
            ),
            external_id=youtube_details.video_id,
            metadata={"channel_name": youtube_details.channel_name},
        )

    @staticmethod
    def to_article_response(
        content: GeneratedContent,
        source_detail: CandidateSourceDetail,
        interactions: List[GeneratedContentInteraction] = [],
    ) -> ArticleResponse:
        return ArticleResponse(
            id=content.id,
            external_id=content.external_id,
            content_type=content.content_type.value,
            status=content.status.value,
            content_generated_at=content.content_generated_at.timestamp(),
            status_details=[
                NewspaperV2Adaptor.to_status_detail(d) for d in content.status_details
            ],
            category=NewspaperV2Adaptor.to_category_info(content.category),
            generated={
                k: NewspaperV2Adaptor.to_generated_data(v)
                for k, v in content.generated.items()
            },
            reading_time_seconds=content.reading_time_seconds,
            created_at=content.created_at.timestamp(),
            updated_at=content.updated_at.timestamp(),
            source_details=NewspaperV2Adaptor.to_source_details(source_detail, content),
            interactions=interactions,
        )

    @staticmethod
    def to_article_response_from_youtube(
        content: GeneratedContent,
        youtube_details: Optional[YouTubeVideoDetails] = None,
        interactions: List[GeneratedContentInteraction] = [],
    ) -> ArticleResponse:
        return ArticleResponse(
            id=content.id,
            external_id=content.external_id,
            content_type=content.content_type.value,
            status=content.status.value,
            content_generated_at=content.content_generated_at.timestamp(),
            status_details=[
                NewspaperV2Adaptor.to_status_detail(d) for d in content.status_details
            ],
            category=NewspaperV2Adaptor.to_category_info(content.category),
            generated={
                k: NewspaperV2Adaptor.to_generated_data(v)
                for k, v in content.generated.items()
            },
            reading_time_seconds=content.reading_time_seconds,
            created_at=content.created_at.timestamp(),
            updated_at=content.updated_at.timestamp(),
            source_details=NewspaperV2Adaptor.to_source_details_from_youtube(
                content, youtube_details
            ),
            interactions=interactions,
        )

    @staticmethod
    def to_newspaper_v2_response(
        newspaper: NewspaperV2,
        articles: List[ArticleResponse],
        has_next: bool,
        next_cursor: str = None,
    ) -> NewspaperV2Response:
        article_list = ArticleV2ListResponse(
            data=articles, hasNext=has_next, nextCursor=next_cursor
        )
        return NewspaperV2Response(
            id=newspaper.id,
            user_id=newspaper.user_id,
            created_at=newspaper.created_at.timestamp(),
            updated_at=newspaper.updated_at.timestamp(),
            status=(
                newspaper.status.value
                if hasattr(newspaper.status, "value")
                else str(newspaper.status)
            ),
            status_details=[
                NewspaperV2Adaptor.to_status_detail(d) for d in newspaper.status_details
            ],
            articles=article_list,
            reading_time_in_seconds=newspaper.reading_time_in_seconds,
        )
