"""
Newspaper article candidate database model for MongoDB.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CandidateStatusDetailDBModel(BaseModel):
    status: str = Field(..., description="Status value")
    created_at: float = Field(..., description="UTC epoch seconds")
    reason: str = Field(default="", description="Status change reason")


class CandidateLinksDBModel(BaseModel):
    user_collected_content_id: Optional[str] = Field(default=None)
    generated_content_id: Optional[str] = Field(default=None)
    generated_content_id_list: List[str] = Field(default_factory=list)


class NewspaperArticleCandidateDBModel(BaseModel):
    id: str = Field(alias="_id", description="MongoDB _id field")
    linked_id: str = Field(..., description="The ID from the source")
    source: str = Field(..., description="The source of the candidate")
    type: str = Field(..., description="The type of the candidate")
    user_id: str = Field(..., description="User ID")
    links: CandidateLinksDBModel = Field(
        ..., description="Links associated with the candidate"
    )
    newspaper_id: Optional[str] = Field(
        default=None, description="The ID of the newspaper this candidate belongs to"
    )
    status: str = Field(..., description="Candidate status")
    status_details: List[CandidateStatusDetailDBModel] = Field(default_factory=list)
    version: int = Field(default=1, description="Version for optimistic locking")
    created_at: float = Field(..., description="UTC epoch seconds")
    updated_at: float = Field(..., description="UTC epoch seconds")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
