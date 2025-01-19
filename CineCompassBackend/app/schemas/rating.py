from pydantic import BaseModel
from datetime import datetime

class RatingBase(BaseModel):
    movie_id: int
    rating: float


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True