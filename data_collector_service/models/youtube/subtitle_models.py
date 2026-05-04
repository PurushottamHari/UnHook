from typing import List

from pydantic import BaseModel


class SubtitleMap(BaseModel):
    """Represents subtitle mapping with language information."""

    language: str
    subtitle: str


class SubtitleData(BaseModel):
    """Contains both automatic and manual subtitle mappings."""

    automatic: List[SubtitleMap]
    manual: List[SubtitleMap]


class DownloadedSubtitleMap(BaseModel):
    """Represents a downloaded subtitle mapping with metadata."""

    language: str
    subtitle: str
    extension: str


class DownloadedSubtitleData(BaseModel):
    """Contains both automatic and manual downloaded subtitle mappings."""

    automatic: List[DownloadedSubtitleMap]
    manual: List[DownloadedSubtitleMap]
