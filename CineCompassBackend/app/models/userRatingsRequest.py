from pydantic import BaseModel
from typing import List
from app.models.rating import Rating

class UserRatingsRequest(BaseModel):
    ratings: List[Rating]
