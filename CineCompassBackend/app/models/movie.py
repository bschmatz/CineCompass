from typing import List
from pydantic import BaseModel

class Movie(BaseModel):
    id: int
    title: str
    genres: List[str]
    cast: List[str]
    director: str