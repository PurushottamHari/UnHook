from pydantic import BaseModel, Field


class CategorizationDataInput(BaseModel):
    id: str = Field(..., description="Unique identifier for the content item")
    title: str = Field(..., description="Title of the content")
    short_summary: str = Field(..., description="Short summary of the content")
