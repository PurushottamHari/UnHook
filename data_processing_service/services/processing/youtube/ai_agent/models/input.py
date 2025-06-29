from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, Field

class SubtitleDataInput(BaseModel):
    language: str
    subtitle_string: str

class ContentDataInput(BaseModel):
    id: str = Field(..., description="Unique identifier for the content item")
    title: str = Field(..., description="Title of the content")
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    subtitle_data_input: SubtitleDataInput