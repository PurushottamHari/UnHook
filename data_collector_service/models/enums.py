from enum import Enum


class ContentType(str, Enum):
    YOUTUBE_VIDEO = "YOUTUBE_VIDEO"
    DISCOVERED_WEBPAGE = "DISCOVERED_WEBPAGE"
