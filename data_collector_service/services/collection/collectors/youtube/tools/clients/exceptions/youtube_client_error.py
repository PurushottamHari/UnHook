class YoutubeClientError(Exception):
    """Base exception for YouTube client errors."""

    def __init__(self, message: str, raw_output: str = ""):
        super().__init__(message)
        self.raw_output = raw_output
