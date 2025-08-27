"""
MongoDB database models for user interests.
"""

from typing import List, Optional

from models.enums import CategoryName, OutputType, Weekday
from pydantic import BaseModel, Field


class InterestDBModel(BaseModel):
    """Database model for user interests."""

    category_name: str  # Stored as string representation of CategoryName
    category_definition: str = Field(..., max_length=500)
    weekdays: List[str]  # Stored as list of string representations of Weekday
    output_type: str  # Stored as string representation of OutputType


class NotInterestedDBModel(BaseModel):
    """Database model for topics user is not interested in."""

    category_definition: str = Field(..., max_length=500)
