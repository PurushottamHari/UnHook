from pydantic import BaseModel
from typing import List


class SubtitleMap(BaseModel):
    """Represents subtitle mapping with language information."""
    language: str
    subtitle: str


class SubtitleData(BaseModel):
    """Contains both automatic and manual subtitle mappings."""
    automatic: List[SubtitleMap]
    manual: List[SubtitleMap]


class SubtitleDataInput(BaseModel):
    language: str
    subtitle_string: str
