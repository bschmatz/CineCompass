from pydantic import BaseModel

class Rating(BaseModel):
    movie_id: int
    rating: float