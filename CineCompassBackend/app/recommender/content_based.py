import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from app.database.database_builder import Movie
from app.database.init_db import init_db

class CineCompassRecommender:
    def __init__(self):
        self.engine, self.Session = init_db()
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = None
        self.movies_df = None
        self.load_data_from_db()

    def load_data_from_db(self):
        with self.Session() as session:
            movies = session.query(Movie).all()
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

    def get_recommendations(self, user_ratings: List[Tuple[int, float]]) -> List[dict]:
        if not user_ratings or self.movies_df is None or self.movies_df.empty:
            return []

        user_profile = np.zeros_like(self.tfidf_matrix.mean(axis=0).A1)
        for movie_id, rating in user_ratings:
            try:
                movie_idx = self.movies_df[self.movies_df["id"] == movie_id].index[0]
                user_profile += self.tfidf_matrix[movie_idx].toarray()[0] * (rating / 5.0)
            except IndexError:
                continue

        # Calculate similarity between user profile and all movies
        similarities = cosine_similarity(
            user_profile.reshape(1, -1),
            self.tfidf_matrix.toarray()
        )[0]

        rated_movie_indices = [
            self.movies_df[self.movies_df["id"] == movie_id].index[0]
            for movie_id, _ in user_ratings
            if not self.movies_df[self.movies_df["id"] == movie_id].empty
        ]
        movie_indices = np.argsort(similarities)[::-1]
        movie_indices = [idx for idx in movie_indices if idx not in rated_movie_indices][:10]

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