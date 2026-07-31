from typing import List

from pydantic import BaseModel, Field


class WebpageStatusDetailDB(BaseModel):
    """Database model for webpage status updates."""

    status: str
    created_at: float
    reason: str = ""


class WebpageCollectedContentDBModel(BaseModel):
    """Database model for storing webpage collected content in MongoDB."""

    id: str = Field(alias="_id")
    sha: str
    url: str
    title: str
    webpage_content: str
    language: str
    category_name: str
    status: str
    status_details: List[WebpageStatusDetailDB]
    created_at: float
    content_created_at: float
    version: int = Field(default=1)

    class Config:
        """Pydantic config."""

        populate_by_name = True
