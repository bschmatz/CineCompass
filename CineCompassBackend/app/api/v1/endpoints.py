from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database.database_builder import CineCompassDatabaseBuilder
from app.recommender.content_based import CineCompassRecommender
from app.auth.deps import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse
from datetime import datetime
from app.schemas.rating import RatingCreate, BatchRatingCreate
from app.schemas.movie import PopularMovie
import uuid

router = APIRouter()

def get_or_create_session(session_id: Optional[str] = Header(None, alias="X-Session-ID"), db: Session = Depends(get_db)) -> User:
    """Get existing session or create a new one"""
    if not session_id:
        session_id = str(uuid.uuid4())

    user = db.query(User).filter(User.session_id == session_id).first()

    if not user:
        user = User(
            session_id=session_id,
            created_at=datetime.utcnow(),
            last_session_refresh=datetime.utcnow()
        )
        db.add(user)
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            user = db.query(User).filter(User.session_id == session_id).first()
            if not user:
                raise HTTPException(status_code=500, detail="Failed to create session")

    return user

@router.get("/")
async def root():
    return {"message": "CineCompass is running"}

@router.post("/init-session")
async def init_session(
    current_user: User = Depends(get_or_create_session)
):
    """Initialize or retrieve session"""
    return {
        "session_id": current_user.session_id,
        "has_finished_onboarding": current_user.has_finished_onboarding
    }

@router.post("/refresh-session")
async def refresh_session(
    current_user: User = Depends(get_or_create_session),
    db: Session = Depends(get_db)
):
    try:
        current_user.last_session_refresh = datetime.utcnow()
        db.commit()

        recommender = CineCompassRecommender(db)
        await recommender.update_recommendations(current_user.id)

        return {"status": "success", "message": "Session refreshed and recommendations updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/is-onboarded", response_model=bool)
async def is_onboarded(current_user: User = Depends(get_or_create_session)):
    try:
        return current_user.has_finished_onboarding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_builder():
    builder = CineCompassDatabaseBuilder()
    return builder


def get_recommender(db: Session = Depends(get_db)) -> CineCompassRecommender:
    return CineCompassRecommender(db)


@router.post("/ratings")
async def add_rating(
    rating: RatingCreate,
    current_user: User = Depends(get_or_create_session),
    recommender: CineCompassRecommender = Depends(get_recommender)
):
    try:
        return recommender.process_rating(
            user_id=current_user.id,
            movie_id=rating.movie_id,
            rating=rating.rating
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    page: int = 1,
    page_size: int = 20,
    last_sync_time: Optional[str] = None,
    current_user: User = Depends(get_or_create_session),
    recommender: CineCompassRecommender = Depends(get_recommender)
):
    try:
        sync_time = datetime.fromisoformat(last_sync_time) if last_sync_time else None
        return recommender.get_recommendations(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            last_sync_time=sync_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/movies/popular", response_model=List[PopularMovie])
async def get_popular_movies(
        limit: int = 10,
        recommender: CineCompassRecommender = Depends(get_recommender)
):
    try:
        return recommender.get_popular_movies(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ratings/batch")
async def add_batch_ratings(
        ratings: BatchRatingCreate,
        current_user: User = Depends(get_or_create_session),
        recommender: CineCompassRecommender = Depends(get_recommender)
):
    try:
        if len(ratings.ratings) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 ratings can be submitted at once"
            )

        return recommender.process_batch_ratings(
            user_id=current_user.id,
            ratings=ratings.ratings
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))