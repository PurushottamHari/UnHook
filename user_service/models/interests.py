"""
Models for user interests and preferences.
"""

from typing import List

from pydantic import BaseModel, Field, validator

from .enums import CategoryName, OutputType, Weekday


class NotInterested(BaseModel):
    category_definition: str = Field(..., max_length=200)


class Interest(BaseModel):
    category_name: CategoryName
    category_definition: str = Field(..., max_length=200)
    weekdays: List[Weekday]
    output_type: OutputType

    @validator("weekdays")
    def validate_weekdays(cls, v):
        if not v:
            raise ValueError("At least one weekday must be specified")
        return v
