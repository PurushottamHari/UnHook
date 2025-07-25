"""
MongoDB database model for generated content.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class StatusDetailDBModel(BaseModel):
    status: str
    created_at: float
    reason: str = ""


class GeneratedDataDBModel(BaseModel):
    markdown_string: str = ""
    string: str = ""


class CategoryInfoDBModel(BaseModel):
    category: str
    category_description: str = ""
    category_tags: list[str] = []


class GeneratedContentDBModel(BaseModel):
    """Database model for generated content."""

    id: str = Field(alias="_id")  # MongoDB _id field
    external_id: str
    content_type: str
    generated: Dict[str, GeneratedDataDBModel] = {}
    reading_time_seconds: int = 0
    created_at: float
    updated_at: float
    content_generated_at: float
    status: str
    status_details: list[StatusDetailDBModel]
    category: Optional[CategoryInfoDBModel] = None

    class Config:
        populate_by_name = True
