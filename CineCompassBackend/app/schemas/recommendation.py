from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RecommendationItem(BaseModel):
    id: int
    title: str
    similarity_score: float
    genres: List[str]
    cast: List[str]
    director: str

class RecommendationResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    needs_sync: Optional[bool] = False
    new_ratings: Optional[List[Dict[str, Any]]] = None