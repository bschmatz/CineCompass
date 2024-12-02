from fastapi import APIRouter, HTTPException

from app.models.userRatingsRequest import UserRatingsRequest
from app.recommender.content_based import MovieRecommender

router = APIRouter()
recommender = MovieRecommender()

@router.post("/recommendations/")
async def get_recommendations(request: UserRatingsRequest):
    try:
        user_ratings = [(rating.movie_id, rating.rating) for rating in request.ratings]
        recommendations = recommender.get_recommendations(user_ratings)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movies/{movie_id}")
async def get_movie(movie_id: int):
    try:
        movie = recommender.get_movie_details(movie_id)
        return movie
    except Exception as e:
        raise HTTPException(status_code=404, detail="Movie not found")