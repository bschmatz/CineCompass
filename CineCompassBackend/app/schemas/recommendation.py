from pydantic import BaseModel
from typing import List

class RecommendationResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int