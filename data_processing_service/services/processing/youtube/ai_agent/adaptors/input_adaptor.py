from typing import List, Optional

from data_collector_service.collectors.youtube.models.youtube_video_details import (
    YouTubeVideoDetails,
)
from data_processing_service.models.youtube.subtitle_data import SubtitleMap
from data_processing_service.services.processing.youtube.ai_agent.models.input import (
    ContentDataInput,
    SubtitleDataInput,
)


class ContentInputAdaptor:
    @staticmethod
    def from_youtube_details_and_subtitle_map(
        youtube_video_details: YouTubeVideoDetails, subtitle_map: SubtitleMap
    ) -> ContentDataInput:
        subtitle_data_input = SubtitleDataInput(
            language=subtitle_map.language, subtitle_string=subtitle_map.subtitle
        )
        return ContentDataInput(
            id=youtube_video_details.video_id,
            title=youtube_video_details.title,
            tags=youtube_video_details.tags[:5] if youtube_video_details.tags else [],
            categories=(
                youtube_video_details.categories[:5]
                if youtube_video_details.categories
                else []
            ),
            subtitle_data_input=subtitle_data_input,
        )
