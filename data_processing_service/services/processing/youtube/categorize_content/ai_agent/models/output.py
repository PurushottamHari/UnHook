from typing import List

from pydantic import BaseModel, Field


class CategoryOutputItem(BaseModel):
    id: str = Field(..., description="Original id of the content item.")
    category: str = Field(..., description="One of the predefined categories.")
    category_description: str = Field(
        ..., description="1 sentence description of the category."
    )
    category_tags: List[str] = Field(..., description="3-5 tags.")


class CategorizationDataOutput(BaseModel):
    output: List[CategoryOutputItem] = Field(
        ..., description="List of category info objects for each content item."
    )
