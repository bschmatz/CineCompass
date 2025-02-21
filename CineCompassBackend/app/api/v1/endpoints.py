from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Boolean
from sqlalchemy.orm import Session
from app.database.database_builder import CineCompassDatabaseBuilder
from app.recommender.content_based import CineCompassRecommender
from app.auth.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token
from app.schemas.recommendation import RecommendationResponse
from app.auth.jwt_handler import JWTHandler
from datetime import timedelta, datetime
from app.schemas.rating import RatingCreate, BatchRatingCreate
from app.schemas.movie import PopularMovie

router = APIRouter()
jwt_handler = JWTHandler()

@router.get("/")
async def root():
    return {"message": "CineCompass is running"}

@router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not user.verify_password(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user.last_session_refresh = datetime.utcnow()
    db.commit()

    recommender = CineCompassRecommender(db)
    recommender.update_recommendations(user.id)

    access_token = jwt_handler.create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(days=1))

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/refresh-session")
async def refresh_session(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        current_user.last_session_refresh = datetime.utcnow()
        db.commit()

        recommender = CineCompassRecommender(db)
        recommender.update_recommendations(current_user.id)

        return {"status": "success", "message": "Session refreshed and recommendations updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/is-onboarded", response_model=bool)
async def login(current_user: User = Depends(get_current_user)):
    try:
        test = current_user.has_finished_onboarding
        return test
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=User.hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = jwt_handler.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=1)
    )

    return {"access_token": access_token, "token_type": "bearer"}


def get_builder():
    builder = CineCompassDatabaseBuilder()
    return builder


def get_recommender(db: Session = Depends(get_db)) -> CineCompassRecommender:
    return CineCompassRecommender(db)


@router.post("/ratings")
async def add_rating(
    rating: RatingCreate,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
        current_user: User = Depends(get_current_user),
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
