import uuid
from typing import List

from commons.infra.dependency_injection.injectable import injectable
from data_collector_service.models.enums import ContentType
from data_collector_service.models.user_collected_content import (
    ContentStatus, StatusDetail, UserCollectedContent)
from data_collector_service.models.youtube.youtube_video_details import \
    YouTubeVideoDetails


@injectable()
class YouTubeToUserContentAdapter:
    """Adapter to convert YouTube video details to user collected content."""

    @staticmethod
    def convert(
        video: YouTubeVideoDetails, user_id: str, include_data: bool = True
    ) -> UserCollectedContent:
        """
        Convert a YouTube video to user collected content.

        Args:
            video: YouTubeVideoDetails object
            user_id: ID of the user
            include_data: Whether to include the raw video data in the response.
                          Defaults to True for backward compatibility.

        Returns:
            UserCollectedContent object
        """
        generated_id = str(uuid.uuid4())
        content_created_at = (
            video.release_date if video.release_date else video.created_at
        )
        return UserCollectedContent(
            id=generated_id,
            content_type=ContentType.YOUTUBE_VIDEO,
            user_id=user_id,
            external_id=video.video_id,
            output_type="youtube_video",
            created_at=video.created_at,
            content_created_at=content_created_at,
            updated_at=video.created_at,
            status=ContentStatus.COLLECTED,
            status_details=[
                StatusDetail(
                    status=ContentStatus.COLLECTED,
                    created_at=video.created_at,
                    reason="Video collected from YouTube",
                )
            ],
            data={},
        )

    @staticmethod
    def convert_batch(
        videos: List[YouTubeVideoDetails], user_id: str, include_data: bool = True
    ) -> List[UserCollectedContent]:
        """
        Convert a list of YouTube videos to user collected content.

        Args:
            videos: List of YouTubeVideoDetails objects
            user_id: ID of the user
            include_data: Whether to include the raw video data in the response.

        Returns:
            List of UserCollectedContent objects
        """
        return [
            YouTubeToUserContentAdapter.convert(video, user_id, include_data)
            for video in videos
        ]
