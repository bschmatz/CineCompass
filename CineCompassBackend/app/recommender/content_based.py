import os

import numpy as np
from pyexpat import features
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rating import Rating
from app.models.cached_recommendation import CachedRecommendation
from app.models.movie import Movie
from app.schemas.rating import RatingCreate
from app.schemas.recommendation import RecommendationResponse
import pandas as pd
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

load_dotenv()

class CineCompassRecommender:
    def __init__(self, db: Session):
        self.db = db
        max_features = 1000 if os.getenv("IS_PRODUCTION") == "true" else 2000
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=max_features,
            min_df=3,
            max_df=0.95,
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.movies_df = None
        self.last_update_time = {}
        self.update_threshold = timedelta(hours=4)
        self.similarity_cache = {}
        self.scaler = MinMaxScaler()
        self._load_movies()

    def _load_movies(self):
        try:
            movies = self.db.query(Movie).all()
            if movies:
                self.movies_df = pd.DataFrame([{
                    'id': movie.id,
                    'title': movie.title,
                    'combined_features': self._preprocess_features(movie),
                    'details': {
                        'genres': movie.genres,
                        'cast': movie.cast,
                        'director': movie.director,
                        'poster_path': movie.poster_path,
                        'backdrop_path': movie.backdrop_path,
                        'overview': movie.overview,
                        'vote_average': movie.vote_average,
                        'popularity': movie.popularity
                    }
                } for movie in movies])

                if not self.movies_df.empty:
                    self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
                        self.movies_df['combined_features']
                    ).tocsr()
                    self._precompute_popular_similarities()
        except Exception as e:
            logger.error(f"Error loading movies: {str(e)}")
            raise

    def _preprocess_features(self, movie: Movie) -> str:
        features = []

        if movie.genres:
            features.extend([f"genre_{g.lower()}" * 3 for g in movie.genres])

        if movie.director:
            features.append(f"director_{movie.director.lower()}" * 2)

        if movie.cast:
            for i, actor in enumerate(movie.cast[:5]):
                weight = 5 - i
                features.extend([f"actor_{actor.lower()}" * weight])

        if movie.overview:
            cleaned_overview = movie.overview.lower()
            for phrase in ["the movie", "the film", "the story"]:
                cleaned_overview = cleaned_overview.replace(phrase, "")
            features.append(cleaned_overview)

        return " ".join(features)

    def _precompute_popular_similarities(self):
        popular_movies = (
            self.db.query(Movie.id)
            .order_by(Movie.popularity.desc())
            .limit(100)
            .all()
        )

        for movie_id, in popular_movies:
            try:
                movie_idx = self.movies_df[self.movies_df["id"] == movie_id].index[0]
                similarities = cosine_similarity(
                    self.tfidf_matrix[movie_idx:movie_idx + 1],
                    self.tfidf_matrix
                )[0]
                self.similarity_cache[movie_id] = similarities
            except IndexError:
                continue

    def _calculate_diversity_score(self, recommended_movies: List[Dict]) -> float:
        if not recommended_movies:
            return 0.0

        genres = set()
        directors = set()

        for movie in recommended_movies:
            genres.update(movie['genres'])
            directors.add(movie['director'])

        max_genres = len(genres) / (len(recommended_movies) * 3)
        max_directors = len(directors) / len(recommended_movies)

        return (max_genres + max_directors) / 2

    def _get_user_preferences(self, user_id: int) -> Tuple[Dict, Dict]:
        ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()

        genre_preferences = {}
        director_preferences = {}

        for rating in ratings:
            movie = self.db.query(Movie).filter(Movie.id == rating.movie_id).first()
            if movie:
                for genre in movie.genres:
                    if genre not in genre_preferences:
                        genre_preferences[genre] = {'count': 0, 'avg_rating': 0}
                    genre_preferences[genre]['count'] += 1
                    genre_preferences[genre]['avg_rating'] = (
                            (genre_preferences[genre]['avg_rating'] * (genre_preferences[genre]['count'] - 1) +
                             rating.rating) / genre_preferences[genre]['count']
                    )

                director = movie.director
                if director not in director_preferences:
                    director_preferences[director] = {'count': 0, 'avg_rating': 0}
                director_preferences[director]['count'] += 1
                director_preferences[director]['avg_rating'] = (
                        (director_preferences[director]['avg_rating'] * (director_preferences[director]['count'] - 1) +
                         rating.rating) / director_preferences[director]['count']
                )

        return genre_preferences, director_preferences

    def process_rating(self, user_id: int, movie_id: int, rating: float) -> Dict[str, Any]:
        try:
            existing_rating = (
                self.db.query(Rating)
                .filter(Rating.user_id == user_id, Rating.movie_id == movie_id)
                .first()
            )

            if existing_rating:
                existing_rating.rating = rating
                existing_rating.timestamp = datetime.utcnow()
            else:
                db_rating = Rating(
                    user_id=user_id,
                    movie_id=movie_id,
                    rating=rating,
                    timestamp=datetime.utcnow()
                )
                self.db.add(db_rating)

            self.db.commit()
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
            last_sync_time: Optional[datetime] = None,
            diversity_threshold: float = 0.3
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

            expanded_page_size = int(page_size * 1.5)

            recommendations = (self.db.query(CachedRecommendation)
                               .filter(CachedRecommendation.user_id == user_id)
                               .order_by(CachedRecommendation.similarity_score.desc())
                               .offset((page - 1) * page_size)
                               .limit(expanded_page_size)
                               .all())

            rec_items = [{
                "id": rec.movie_id,
                "similarity_score": rec.similarity_score,
                **rec.details
            } for rec in recommendations]

            diversity_score = self._calculate_diversity_score(rec_items)
            if diversity_score < diversity_threshold:
                alternative_recs = (self.db.query(CachedRecommendation)
                                    .filter(CachedRecommendation.user_id == user_id)
                                    .order_by(func.random())
                                    .limit(expanded_page_size)
                                    .all())

                alt_items = [{
                    "id": rec.movie_id,
                    "similarity_score": rec.similarity_score,
                    **rec.details
                } for rec in alternative_recs]

                rec_items = self._merge_recommendations(rec_items, alt_items, page_size)

            rec_items = rec_items[:page_size]

            total = self.db.query(CachedRecommendation).filter(
                CachedRecommendation.user_id == user_id
            ).count()

            return RecommendationResponse(
                items=rec_items,
                total=total,
                page=page,
                page_size=page_size,
                diversity_score=diversity_score
            )
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise

    def _merge_recommendations(
            self,
            original_recs: List[Dict],
            alternative_recs: List[Dict],
            target_size: int
    ) -> List[Dict]:
        merged = []
        orig_idx = alt_idx = 0

        while len(merged) < target_size and (orig_idx < len(original_recs) or alt_idx < len(alternative_recs)):
            if orig_idx < len(original_recs):
                merged.append(original_recs[orig_idx])
                orig_idx += 1

            if len(merged) < target_size and alt_idx < len(alternative_recs):
                alt_rec = alternative_recs[alt_idx]
                if alt_rec['id'] not in [m['id'] for m in merged]:
                    merged.append(alt_rec)
                alt_idx += 1

        return merged

    def update_recommendations(self, user_id: int):
        try:
            ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
            if not ratings:
                return

            user_profile = np.zeros_like(self.tfidf_matrix.mean(axis=0).A1)
            rated_movie_indices = []
            recent_weights = []

            genre_prefs, director_prefs = self._get_user_preferences(user_id)

            current_time = datetime.utcnow()
            for rating in ratings:
                try:
                    movie_idx = self.movies_df[self.movies_df["id"] == rating.movie_id].index[0]
                    rated_movie_indices.append(movie_idx)

                    days_old = (current_time - rating.timestamp).days
                    time_weight = 1.0 / (1.0 + np.log1p(days_old))
                    recent_weights.append(time_weight)

                    movie = self.movies_df.iloc[movie_idx]
                    base_weight = rating.rating / 5.0

                    genre_boost = 1.0
                    director_boost = 1.0

                    for genre in movie['details']['genres']:
                        if genre in genre_prefs and genre_prefs[genre]['count'] >= 3:
                            genre_boost += 0.2 * (genre_prefs[genre]['avg_rating'] / 5.0)

                    director = movie['details']['director']
                    if director in director_prefs and director_prefs[director]['count'] >= 2:
                        director_boost += 0.3 * (director_prefs[director]['avg_rating'] / 5.0)

                    final_weight = base_weight * time_weight * genre_boost * director_boost
                    user_profile += self.tfidf_matrix[movie_idx].toarray()[0] * final_weight

                except IndexError:
                    continue

            if not rated_movie_indices:
                return

            user_profile = user_profile / np.linalg.norm(user_profile)

            similarities = cosine_similarity(
                user_profile.reshape(1, -1),
                self.tfidf_matrix.toarray()
            )[0]

            mask = np.ones(len(self.tfidf_matrix.toarray()), dtype=bool)
            mask[rated_movie_indices] = False

            similarities = similarities[mask]
            available_indices = np.where(mask)[0]

            similarities = self.scaler.fit_transform(similarities.reshape(-1, 1)).ravel()

            ranked_indices = np.argsort(similarities)[::-1]

            self.db.query(CachedRecommendation).filter(
                CachedRecommendation.user_id == user_id
            ).delete()

            batch_size = 100
            recommendations = []

            for i, rank_idx in enumerate(ranked_indices):
                movie_idx = available_indices[rank_idx]
                movie = self.movies_df.iloc[movie_idx]

                cached_rec = CachedRecommendation(
                    user_id=user_id,
                    movie_id=int(movie["id"]),
                    similarity_score=float(similarities[rank_idx]),
                    details={
                        "title": movie["title"],
                        "genres": movie["details"]["genres"],
                        "cast": movie["details"]["cast"],
                        "director": movie["details"]["director"],
                        "poster_path": movie["details"]["poster_path"],
                        "backdrop_path": movie["details"]["backdrop_path"],
                        "overview": movie["details"]["overview"],
                        "vote_average": movie["details"]["vote_average"],
                        "popularity": movie["details"]["popularity"]
                    }
                )
                recommendations.append(cached_rec)

                if len(recommendations) >= batch_size:
                    self.db.bulk_save_objects(recommendations)
                    recommendations = []

            if recommendations:
                self.db.bulk_save_objects(recommendations)

            self.db.commit()

        except Exception as e:
            logger.error(f"Error updating recommendations: {str(e)}")
            self.db.rollback()
            raise

    def get_popular_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            popular_movies = (
                self.db.query(Movie)
                .order_by(Movie.popularity.desc())
                .limit(limit)
                .all()
            )

            return [{
                "id": movie.id,
                "title": movie.title,
                "overview": movie.overview,
                "genres": movie.genres,
                "poster_path": movie.poster_path,
                "vote_average": movie.vote_average,
                "popularity": movie.popularity
            } for movie in popular_movies]
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            raise

    def process_batch_ratings(self, user_id: int, ratings: List[RatingCreate]) -> Dict[str, Any]:
        try:
            new_ratings = []
            updated_count = 0

            for rating_data in ratings:
                existing_rating = (
                    self.db.query(Rating)
                    .filter(Rating.user_id == user_id, Rating.movie_id == rating_data.movie_id)
                    .first()
                )

                if existing_rating:
                    existing_rating.rating = rating_data.rating
                    existing_rating.timestamp = datetime.utcnow()
                    updated_count += 1
                else:
                    new_ratings.append(Rating(
                        user_id=user_id,
                        movie_id=rating_data.movie_id,
                        rating=rating_data.rating,
                        timestamp=datetime.utcnow()
                    ))

            if new_ratings:
                self.db.bulk_save_objects(new_ratings)

            self.db.commit()

            self.update_recommendations(user_id)
            self.last_update_time[user_id] = datetime.utcnow()

            return {
                "status": "success",
                "message": f"Successfully processed {len(new_ratings)} new ratings and updated {updated_count} existing ratings"
            }
        except Exception as e:
            logger.error(f"Error processing batch ratings: {str(e)}")
            self.db.rollback()
            raise