from .youtube_client_error import YoutubeClientError


class PremiumYoutubeVideoException(YoutubeClientError):
    """Exception raised when a YouTube video is detected as members-only or premium."""

    def __init__(self, raw_output: str):
        super().__init__(
            "YouTube video is restricted (members-only/premium).", raw_output
        )
