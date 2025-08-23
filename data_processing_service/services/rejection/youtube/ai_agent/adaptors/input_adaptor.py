import ast
from typing import List

from data_collector_service.collectors.youtube.models import \
    YouTubeVideoDetails
from user_service.models.interests import NotInterested

from ..models.content import ContentItem
from ..models.input import ModerationInput


class InputAdaptor:
    @staticmethod
    def to_moderation_input(
        not_interested_list: List[NotInterested],
        youtube_video_details_list: List[YouTubeVideoDetails],
    ) -> ModerationInput:
        filter_preferences = []
        for not_interested in not_interested_list:
            filter_preferences.append(not_interested.category_definition)
        content_items = []
        for yvd in youtube_video_details_list:
            tags = yvd.tags
            categories = yvd.categories
            item = ContentItem(
                id=yvd.video_id,
                title=yvd.title,
                tags=tags[:5] if tags else None,
                categories=categories[:5] if categories else None,
            )

            content_items.append(item)
        return ModerationInput(
            items=content_items, filter_preferences=filter_preferences
        )
