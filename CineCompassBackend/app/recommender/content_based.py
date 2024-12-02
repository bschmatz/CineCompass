import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from typing import List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class MovieRecommender:
    def __init__(self):
        self.tmdb_access_token = os.getenv("TMDB_ACCESS_TOKEN")
        self.movies_df = None
        self.tfidf_matrix = None
        self.initialize_data()

    def initialize_data(self):
        # todo: load from cache or database, not always from api
        self.fetch_initial_movies()
        self.prepare_features()

    def fetch_initial_movies(self):
        url = "https://api.themoviedb.org/3/movie/popular"
        headers = {
            "Authorization": f"Bearer {self.tmdb_access_token}",
            "accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        movies = response.json()["results"]

        self.movies_df = pd.DataFrame(movies)
        self.movies_df["details"] = self.movies_df["id"].apply(self.get_movie_details)

    def prepare_features(self):
        self.movies_df["combined_features"] = self.movies_df.apply(
            lambda x: f"{x['title']} {x['overview']} {' '.join(x['details']['genres'])} "
                      f"{' '.join(x['details']['cast'])} {x['details']['director']}",
            axis=1
        )

        # Create tfidf matrix to filter out common words and put more weight on unique words: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
        tfidf = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = tfidf.fit_transform(self.movies_df["combined_features"])

    def get_movie_details(self, movie_id: int) -> dict:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        headers = {
            "Authorization": f"Bearer {os.getenv('TMDB_ACCESS_TOKEN')}",
            "accept": "application/json"
        }
        params = {
            "language": "en-US",
            "append_to_response": "credits"
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        return {
            "genres": [g["name"] for g in data.get("genres", [])],
            "cast": [c["name"] for c in data.get("credits", {}).get("cast", [])[:5]],
            "director": next(
                (c["name"] for c in data.get("credits", {}).get("crew", [])
                 if c["job"] == "Director"),
                "Unknown"
            )
        }

    def get_recommendations(self, user_ratings: List[Tuple[int, float]]) -> List[dict]:
        if not user_ratings:
            return []

        # Create user profile of the same shape as the tfidf matrix
        user_profile = np.zeros_like(self.tfidf_matrix.mean(axis=0).A1)

        # Calculate weighted average of movie features based on ratings -> Taste Profile of User
        for movie_id, rating in user_ratings:
            movie_idx = self.movies_df[self.movies_df["id"] == movie_id].index[0]
            user_profile += self.tfidf_matrix[movie_idx].toarray()[0] * (rating / 5.0)

        # Calculate similarity between user profile and all movies
        similarities = cosine_similarity(
            user_profile.reshape(1, -1),
            self.tfidf_matrix.toarray()
        )[0]

        rated_movie_indices = [
            self.movies_df[self.movies_df["id"] == movie_id].index[0]
            for movie_id, _ in user_ratings
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