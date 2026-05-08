from typing import List, Optional

from pydantic import BaseModel

from .article_response import ArticleV2ListResponse, StatusDetail


class NewspaperV2Response(BaseModel):
    id: str
    user_id: str
    created_at: float
    updated_at: float
    status: str
    status_details: List[StatusDetail] = []
    articles: ArticleV2ListResponse
    reading_time_in_seconds: int = 0
