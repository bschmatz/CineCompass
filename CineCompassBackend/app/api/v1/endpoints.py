from app.database.database_builder import CineCompassDatabaseBuilder
from app.models.userRatingsRequest import UserRatingsRequest
from app.recommender.content_based import CineCompassRecommender
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

def get_builder():
    builder = CineCompassDatabaseBuilder()
    return builder

def get_recommender():
    recommender = CineCompassRecommender()
    return recommender

@router.post("/recommendations/")
async def get_recommendations(
    request: UserRatingsRequest,
    recommender: CineCompassRecommender = Depends(get_recommender)
):
    try:
        user_ratings = [(rating.movie_id, rating.rating) for rating in request.ratings]
        recommendations = recommender.get_recommendations(user_ratings)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/populate-database")
async def populate_database(
    target_size: int = 1000,
    builder: CineCompassDatabaseBuilder = Depends(get_builder)
):
    try:
        builder.populate_database(target_size=target_size)
        return {"message": "Database population completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))