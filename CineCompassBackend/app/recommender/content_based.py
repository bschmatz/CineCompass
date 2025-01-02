import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from datetime import datetime
import logging
from app.models.movie import Movie
from app.models.cached_recommendation import CachedRecommendation
from app.database.init_db import init_db
from app.schemas.recommendation import RecommendationResponse


class CineCompassRecommender:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing CineCompassRecommender")

        self.engine, self.Session = init_db()
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self.movies_df = None
        self.load_data_from_db()

    def load_data_from_db(self):
        try:
            self.logger.info("Loading data from database")
            with self.Session() as session:
                movies = session.query(Movie).all()
                self.logger.info(f"Found {len(movies)} movies in database")

                if movies:
                    self.logger.info("Converting movies to DataFrame")
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
                        self.logger.info("Creating TF-IDF matrix")
                        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                            self.movies_df['combined_features']
                        )
                        self.logger.info("TF-IDF matrix created successfully")
                else:
                    self.logger.error("No movies found in database")
        except Exception as e:
            self.logger.error(f"Error in load_data_from_db: {str(e)}")
            raise

    def get_cached_recommendations(self, user_id: int, page: int = 1, page_size: int = 10) -> RecommendationResponse:
        with self.Session() as session:
            total = session.query(CachedRecommendation) \
                .filter(CachedRecommendation.user_id == user_id) \
                .count()

            cached_recommendations = session.query(CachedRecommendation) \
                .filter(CachedRecommendation.user_id == user_id) \
                .order_by(CachedRecommendation.similarity_score.desc()) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()

            items = [
                {
                    "id": rec.movie_id,
                    "similarity_score": rec.similarity_score,
                    **rec.details
                }
                for rec in cached_recommendations
            ]

            return RecommendationResponse(
                items=items,
                total=total,
                page=page,
                page_size=page_size
            )

    def cache_recommendations(self, user_id: int, recommendations: List[dict]):
        with self.Session() as session:
            session.query(CachedRecommendation) \
                .filter(CachedRecommendation.user_id == user_id) \
                .delete()

            for rec in recommendations:
                cached_rec = CachedRecommendation(
                    user_id=user_id,
                    movie_id=rec["id"],
                    similarity_score=rec["similarity_score"],
                    details={
                        "title": rec["title"],
                        "genres": rec["genres"],
                        "cast": rec["cast"],
                        "director": rec["director"]
                    }
                )
                session.add(cached_rec)

            session.commit()

    def calculate_recommendations(self, user_ratings: List[Tuple[int, float]]) -> List[dict]:
        try:
            self.logger.info(f"Getting recommendations for {len(user_ratings)} user ratings")

            if not user_ratings or self.movies_df is None or self.movies_df.empty:
                self.logger.warning("No user ratings or empty movies database")
                return []

            self.logger.info("Creating user profile")
            user_profile = np.zeros_like(self.tfidf_matrix.mean(axis=0).A1)
            for movie_id, rating in user_ratings:
                try:
                    movie_idx = self.movies_df[self.movies_df["id"] == movie_id].index[0]
                except IndexError:
                    self.logger.warning(f"Movie ID {movie_id} not found in database")
                    continue
                user_profile += self.tfidf_matrix[movie_idx].toarray()[0] * (rating / 5.0)

            self.logger.info("Calculating similarities")
            similarities = cosine_similarity(
                user_profile.reshape(1, -1),
                self.tfidf_matrix.toarray()
            )[0]

            self.logger.info("Finding rated movie indices")
            rated_movie_indices = []
            for movie_id, _ in user_ratings:
                movie_indices = self.movies_df[self.movies_df["id"] == movie_id].index
                if not movie_indices.empty:
                    rated_movie_indices.append(movie_indices[0])

            self.logger.info("Sorting and filtering recommendations")
            movie_indices = np.argsort(similarities)[::-1]
            movie_indices = [idx for idx in movie_indices if idx not in rated_movie_indices]

            self.logger.info("Building recommendation list")
            recommendations = []
            for idx in movie_indices:
                movie = self.movies_df.iloc[idx]
                recommendations.append({
                    "id": int(movie["id"]),
                    "title": movie["title"],
                    "similarity_score": float(similarities[idx]),
                    "genres": movie["details"]["genres"],
                    "cast": movie["details"]["cast"],
                    "director": movie["details"]["director"]
                })

            return recommendations

        except Exception as e:
            self.logger.error(f"Error in calculate_recommendations: {str(e)}")
            raise

    def get_recommendations(self, user_id: int, user_ratings: List[Tuple[int, float]], force_refresh: bool = False) -> \
    List[dict]:
        try:
            if not force_refresh:
                with self.Session() as session:
                    cached = session.query(CachedRecommendation) \
                        .filter(CachedRecommendation.user_id == user_id) \
                        .first()

                    if cached and (datetime.utcnow() - cached.created_at).days < 1:
                        self.logger.info("Using cached recommendations")
                        return self.get_cached_recommendations(user_id)

            recommendations = self.calculate_recommendations(user_ratings)

            self.cache_recommendations(user_id, recommendations)

            return recommendations

        except Exception as e:
            self.logger.error(f"Error in get_recommendations: {str(e)}")
            raise