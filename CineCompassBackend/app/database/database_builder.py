import pandas as pd
import requests
from typing import List, Set, Optional
import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import time
import logging
from app.database.init_db import init_db
from app.models.movie import Movie

load_dotenv()
Base = declarative_base()

class CineCompassDatabaseBuilder:
    def __init__(self):
        self.tmdb_access_token = os.getenv("TMDB_ACCESS_TOKEN")
        self.engine, self.Session = init_db()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.processed_movies: Set[int] = set()
        self.load_processed_movies()

    def load_processed_movies(self):
        with self.Session() as session:
            movie_ids = session.query(Movie.id).all()
            self.processed_movies = set(id[0] for id in movie_ids)
        self.logger.info(f"Loaded {len(self.processed_movies)} existing movie IDs")

    def fetch_movies_from_list(self, list_type: str, max_pages: int = 5) -> List[dict]:
        movies = []
        page = 1

        while page <= max_pages:
            url = f"https://api.themoviedb.org/3/movie/{list_type}"
            headers = {
                "Authorization": f"Bearer {self.tmdb_access_token}",
                "accept": "application/json"
            }
            params = {"page": page}

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                new_movies = [
                    movie for movie in data["results"]
                    if movie["id"] not in self.processed_movies
                ]

                if not new_movies:
                    self.logger.info(f"No new movies found in {list_type} page {page}")
                    break

                movies.extend(new_movies)
                self.logger.info(f"Fetched {len(new_movies)} new movies from {list_type} page {page}")

                time.sleep(0.25)
                page += 1

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching {list_type} page {page}: {str(e)}")
                break

        return movies

    def get_movie_details(self, movie_id: int) -> Optional[dict]:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        headers = {
            "Authorization": f"Bearer {self.tmdb_access_token}",
            "accept": "application/json"
        }
        params = {
            "language": "en-US",
            "append_to_response": "credits"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
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

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching details for movie {movie_id}: {str(e)}")
            return None

    @staticmethod
    def create_combined_features(title: str, overview: str, genres: List[str],
                                 cast: List[str], director: str) -> str:
        """Create combined features string for TF-IDF"""
        return f"{title} {overview} {' '.join(genres)} {' '.join(cast)} {director}"

    def process_movies_batch(self, movies: List[dict], batch_size: int = 10) -> int:
        processed_count = 0

        for i in range(0, len(movies), batch_size):
            self.logger.info(f"Processing batch {i // batch_size + 1} out of {len(movies) // batch_size + 1}")
            batch = movies[i:i + batch_size]
            with self.Session() as session:
                for movie_data in batch:
                    if movie_data["id"] in self.processed_movies:
                        continue

                    details = self.get_movie_details(movie_data["id"])
                    if not details:
                        continue

                    combined_features = self.create_combined_features(
                        movie_data["title"],
                        movie_data.get("overview", ""),
                        details["genres"],
                        details["cast"],
                        details["director"]
                    )

                    movie = Movie(
                        id=movie_data["id"],
                        title=movie_data["title"],
                        overview=movie_data.get("overview", ""),
                        genres=details["genres"],
                        cast=details["cast"],
                        director=details["director"],
                        popularity=movie_data.get("popularity", 0),
                        vote_average=movie_data.get("vote_average", 0),
                        last_updated=datetime.now(),
                        combined_features=combined_features
                    )

                    session.merge(movie)
                    self.processed_movies.add(movie_data["id"])
                    processed_count += 1

                session.commit()

            time.sleep(0.25)

        return processed_count

    def populate_database(self, target_size: int = 1000):
        current_size = len(self.processed_movies)
        self.logger.info(f"Current database size: {current_size}")

        if current_size >= target_size:
            self.logger.info("Database already meets target size")
            return

        sources = ["popular", "top_rated", "now_playing"]
        max_pages_per_source = 50

        for source in sources:
            if len(self.processed_movies) >= target_size:
                break

            self.logger.info(f"Fetching movies from {source}")
            movies = self.fetch_movies_from_list(source, max_pages_per_source)

            if movies:
                processed = self.process_movies_batch(movies)
                self.logger.info(f"Processed {processed} new movies from {source}")

            current_size = len(self.processed_movies)
            self.logger.info(f"Current database size: {current_size}")

    def update_existing_movies(self, days_threshold: int = 30):
        with self.Session() as session:
            outdated_movies = session.query(Movie).filter(
                Movie.last_updated < datetime.now() - pd.Timedelta(days=days_threshold)
            ).all()

            for movie in outdated_movies:
                details = self.get_movie_details(movie.id)
                if details:
                    movie.genres = details["genres"]
                    movie.cast = details["cast"]
                    movie.director = details["director"]
                    movie.last_updated = datetime.now()
                    movie.combined_features = self.create_combined_features(
                        movie.title, movie.overview, details["genres"],
                        details["cast"], details["director"]
                    )
                    self.logger.info(f"Updated movie: {movie.title}")
                time.sleep(0.25)  # Rate limiting

            session.commit()
