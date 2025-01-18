from pydantic import BaseModel
from typing import List
from app.models.rating import Rating

class RecommendationRequest(BaseModel):
    ratings: List[Rating]
    page: int = 1
    page_size: int = 25
    force_refresh: bool = False