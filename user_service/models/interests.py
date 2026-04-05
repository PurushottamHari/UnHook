"""
Models for user interests and preferences.
"""

from typing import List

from pydantic import BaseModel, Field, validator

from .enums import CategoryName, OutputType, Weekday


class NotInterested(BaseModel):
    category_definition: str = Field(..., max_length=500)


class Interest(BaseModel):
    category_name: CategoryName
    category_definition: str = Field(..., max_length=500)
    output_type: OutputType
