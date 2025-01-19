from pydantic import BaseModel
from typing import List, Optional

class PopularMovie(BaseModel):
    id: int
    title: str
    overview: str
    genres: List[str]
    poster_path: Optional[str]
    vote_average: float
    popularity: float