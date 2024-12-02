from fastapi import APIRouter, HTTPException

from app.database.database_builder import CineCompassDatabaseBuilder
from app.models.userRatingsRequest import UserRatingsRequest
from app.recommender.content_based import CineCompassRecommender

router = APIRouter()
builder = CineCompassDatabaseBuilder()
recommender = CineCompassRecommender()

@router.post("/recommendations/")
async def get_recommendations(request: UserRatingsRequest):
    try:
        user_ratings = [(rating.movie_id, rating.rating) for rating in request.ratings]
        recommendations = recommender.get_recommendations(user_ratings)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/populate-database")
async def populate_database(target_size: int = 1000):
    try:
        builder.populate_database(target_size=target_size)
        # Reload recommender data after population
        recommender.load_data_from_db()
        return {"message": "Database population completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/update-movies")
async def update_movies(days_threshold: int = 30):
    try:
        builder.update_existing_movies(days_threshold)
        # Reload recommender data after updates
        recommender.load_data_from_db()
        return {"message": "Movie updates completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))