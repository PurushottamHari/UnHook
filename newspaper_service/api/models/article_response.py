from typing import Dict, List, Optional

from pydantic import BaseModel

from ...models.generated_content_interaction import GeneratedContentInteraction


class SourceDetails(BaseModel):
    type: str
    external_id: str
    metadata: Dict[str, str] = {}


class StatusDetail(BaseModel):
    status: str
    created_at: float
    reason: str = ""


class GeneratedData(BaseModel):
    markdown_string: str = ""
    string: str = ""


class CategoryInfo(BaseModel):
    category: str
    category_description: str = ""
    category_tags: List[str] = []
    shelf_life: Optional[str] = None
    geography: Optional[str] = None


class ArticleResponse(BaseModel):
    id: str
    external_id: str
    content_type: str
    status: str
    content_generated_at: float
    status_details: List[StatusDetail] = []
    category: Optional[CategoryInfo] = None
    generated: Dict[str, GeneratedData] = {}
    reading_time_seconds: int = 0
    created_at: float
    updated_at: float
    source_details: Optional[SourceDetails] = None
    interactions: List[GeneratedContentInteraction] = []


class ArticleV2ListResponse(BaseModel):
    data: List[ArticleResponse] = []
    hasNext: bool = False
    nextCursor: Optional[str] = None
