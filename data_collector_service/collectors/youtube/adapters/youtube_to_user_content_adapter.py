import uuid
from typing import List

from ....models.enums import ContentType
from ....models.user_collected_content import (ContentStatus, StatusDetail,
                                               UserCollectedContent)
from ..models.youtube_video_details import YouTubeVideoDetails


class YouTubeToUserContentAdapter:
    """Adapter to convert YouTube video details to user collected content."""

    @staticmethod
    def convert(video: YouTubeVideoDetails, user_id: str) -> UserCollectedContent:
        """
        Convert a YouTube video to user collected content.

        Args:
            video: YouTubeVideoDetails object
            user_id: ID of the user

        Returns:
            UserCollectedContent object
        """
        generated_id = str(uuid.uuid4())
        return UserCollectedContent(
            id=generated_id,
            content_type=ContentType.YOUTUBE_VIDEO,
            user_id=user_id,
            external_id=video.video_id,
            output_type="youtube_video",
            created_at=video.created_at,
            updated_at=video.created_at,
            status=ContentStatus.COLLECTED,
            status_details=[
                StatusDetail(
                    status=ContentStatus.COLLECTED,
                    created_at=video.created_at,
                    reason="Video collected from YouTube",
                )
            ],
            data={ContentType.YOUTUBE_VIDEO: video},
        )

    @staticmethod
    def convert_batch(
        videos: List[YouTubeVideoDetails], user_id: str
    ) -> List[UserCollectedContent]:
        """
        Convert a list of YouTube videos to user collected content.

        Args:
            videos: List of YouTubeVideoDetails objects
            user_id: ID of the user

        Returns:
            List of UserCollectedContent objects
        """
        return [YouTubeToUserContentAdapter.convert(video, user_id) for video in videos]
