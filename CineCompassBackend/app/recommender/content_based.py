import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from app.models.rating import Rating
from app.models.cached_recommendation import CachedRecommendation
from app.models.movie import Movie
from app.schemas.recommendation import RecommendationResponse
import pandas as pd

logger = logging.getLogger(__name__)

class CineCompassRecommender:
    def __init__(self, db: Session):
        self.db = db
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self.movies_df = None
        self.last_update_time = {}
        self.update_threshold = timedelta(hours=4)
        self._load_movies()

    def _load_movies(self):
        try:
            movies = self.db.query(Movie).all()
            if movies:
                self.movies_df = pd.DataFrame([{
                    'id': movie.id,
                    'title': movie.title,
                    'combined_features': movie.combined_features,
                    'details': {
                        'genres': movie.genres,
                        'cast': movie.cast,
                        'director': movie.director
                    }
                } for movie in movies])

                if not self.movies_df.empty:
                    self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                        self.movies_df['combined_features']
                    )
        except Exception as e:
            logger.error(f"Error loading movies: {str(e)}")
            raise

    def process_rating(self, user_id: int, movie_id: int, rating: float) -> Dict[str, Any]:
        try:
            db_rating = Rating(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating,
                timestamp=datetime.utcnow()
            )
            self.db.add(db_rating)
            self.db.commit()

            last_update = self.last_update_time.get(user_id)
            if not last_update or datetime.utcnow() - last_update > self.update_threshold:
                self._update_recommendations(user_id)
                self.last_update_time[user_id] = datetime.utcnow()

            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error processing rating: {str(e)}")
            self.db.rollback()
            raise

    def get_recommendations(
            self,
            user_id: int,
            page: int = 1,
            page_size: int = 20,
            last_sync_time: Optional[datetime] = None
    ) -> RecommendationResponse:
        try:
            if last_sync_time:
                new_ratings = self.db.query(Rating).filter(
                    Rating.user_id == user_id,
                    Rating.timestamp > last_sync_time
                ).all()

                if new_ratings:
                    return RecommendationResponse(
                        items=[],
                        total=0,
                        page=page,
                        page_size=page_size,
                        needs_sync=True,
                        new_ratings=[rating.to_dict() for rating in new_ratings]
                    )

            total = self.db.query(CachedRecommendation).filter(CachedRecommendation.user_id == user_id).count()

            recommendations = (self.db.query(CachedRecommendation)
                               .filter(CachedRecommendation.user_id == user_id)
                               .order_by(CachedRecommendation.similarity_score.desc())
                               .offset((page - 1) * page_size)
                               .limit(page_size)
                               .all())

            return RecommendationResponse(
                items=[{
                    "id": rec.movie_id,
                    "similarity_score": rec.similarity_score,
                    **rec.details
                } for rec in recommendations],
                total=total,
                page=page,
                page_size=page_size
            )
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise

    def _update_recommendations(self, user_id: int):
        try:
            ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
            if not ratings:
                return

            user_profile = np.zeros_like(self.tfidf_matrix.mean(axis=0).A1)
            rated_movie_indices = []

            for rating in ratings:
                try:
                    movie_idx = self.movies_df[self.movies_df["id"] == rating.movie_id].index[0]
                    rated_movie_indices.append(movie_idx)
                    user_profile += self.tfidf_matrix[movie_idx].toarray()[0] * (rating.rating / 5.0)
                except IndexError:
                    continue

            similarities = cosine_similarity(
                user_profile.reshape(1, -1),
                self.tfidf_matrix.toarray()
            )[0]

            movie_indices = np.argsort(similarities)[::-1]
            movie_indices = [idx for idx in movie_indices if idx not in rated_movie_indices]

            self.db.query(CachedRecommendation).filter(CachedRecommendation.user_id == user_id).delete()

            for idx in movie_indices:
                movie = self.movies_df.iloc[idx]
                cached_rec = CachedRecommendation(
                    user_id=user_id,
                    movie_id=int(movie["id"]),
                    similarity_score=float(similarities[idx]),
                    details={
                        "title": movie["title"],
                        "genres": movie["details"]["genres"],
                        "cast": movie["details"]["cast"],
                        "director": movie["details"]["director"]
                    }
                )
                self.db.add(cached_rec)

            self.db.commit()
        except Exception as e:
            logger.error(f"Error updating recommendations: {str(e)}")
            self.db.rollback()
            raise