import asyncio
import aiohttp
import logging
import os
import math
from typing import List, Set, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database.init_db import init_db
from app.models.movie import Movie

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CineCompassDatabaseBuilder:
    def __init__(self):
        self.tmdb_access_token = os.getenv("TMDB_ACCESS_TOKEN")
        self.engine, self.Session = init_db()
        self.processed_movies: Set[int] = set()
        self.semaphore = asyncio.Semaphore(30) 
        self.load_processed_movies()

    def load_processed_movies(self):
        with self.Session() as session:
            movie_ids = session.query(Movie.id).all()
            self.processed_movies = set(id[0] for id in movie_ids)
        logger.info(f"Loaded {len(self.processed_movies)} existing movie IDs")

    async def fetch_page_async(self, session: aiohttp.ClientSession, list_type: str, page: int) -> List[Dict]:
        """Fetch a single page of movie lists (popular, top_rated, etc)"""
        url = f"https://api.themoviedb.org/3/movie/{list_type}"
        headers = {"Authorization": f"Bearer {self.tmdb_access_token}", "accept": "application/json"}
        params = {"page": page}
        
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    logger.warning(f"Failed to fetch {list_type} page {page}: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching {list_type} page {page}: {e}")
            return []

    async def fetch_movie_details_async(self, session: aiohttp.ClientSession, movie_basic_data: Dict) -> Dict:
        """Fetch details for a specific movie ID"""
        movie_id = movie_basic_data['id']
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        headers = {"Authorization": f"Bearer {self.tmdb_access_token}", "accept": "application/json"}
        params = {"append_to_response": "credits"}

        # Use semaphore to limit concurrency so we don't hit 429 Too Many Requests
        async with self.semaphore:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "basic_data": movie_basic_data,
                            "details": data
                        }
                    elif response.status == 429:
                        logger.warning("Rate limit hit, sleeping briefly...")
                        await asyncio.sleep(1)
                        return None
                    else:
                        return None
            except Exception as e:
                logger.error(f"Error fetching details for {movie_id}: {e}")
                return None

    @staticmethod
    def process_movie_data(data: Dict) -> Movie:
        """Transform raw API data into a Movie object"""
        basic = data['basic_data']
        details = data['details']
        
        genres = [g["name"] for g in details.get("genres", [])]
        # Take top 5 cast
        cast = [c["name"] for c in details.get("credits", {}).get("cast", [])[:5]]
        director = next(
            (c["name"] for c in details.get("credits", {}).get("crew", []) if c["job"] == "Director"), 
            "Unknown"
        )

        combined_features = f"{basic['title']} {basic.get('overview', '')} {' '.join(genres)} {' '.join(cast)} {director}"

        return Movie(
            id=basic["id"],
            title=basic["title"],
            overview=basic.get("overview", ""),
            genres=genres,
            cast=cast,
            director=director,
            popularity=basic.get("popularity", 0),
            vote_average=basic.get("vote_average", 0),
            last_updated=datetime.now(),
            combined_features=combined_features,
            poster_path=basic.get("poster_path"),
            backdrop_path=basic.get("backdrop_path")
        )

    async def run_population_async(self, target_size: int = 5000):
        current_size = len(self.processed_movies)
        if current_size >= target_size:
            logger.info("Database already populated.")
            return

        needed = target_size - current_size
        logger.info(f"Need to fetch approximately {needed} more movies.")

        async with aiohttp.ClientSession() as session:
            sources = ["popular", "top_rated", "now_playing"]
            candidates = []
            
            pages_per_source = math.ceil((needed / 20) / len(sources)) + 5
            
            tasks = []
            for source in sources:
                for page in range(1, pages_per_source + 1):
                    tasks.append(self.fetch_page_async(session, source, page))
            
            logger.info(f"Fetching movie lists from {len(tasks)} pages...")
            results = await asyncio.gather(*tasks)
            
            unique_candidates = {}
            for batch in results:
                for movie in batch:
                    if movie['id'] not in self.processed_movies:
                        unique_candidates[movie['id']] = movie
            
            candidates_list = list(unique_candidates.values())[:needed]
            logger.info(f"Found {len(candidates_list)} unique new movies to process.")

            batch_size = 50
            
            for i in range(0, len(candidates_list), batch_size):
                batch_candidates = candidates_list[i : i + batch_size]
                logger.info(f"Enriching batch {i} to {i + len(batch_candidates)}...")
                
                detail_tasks = [self.fetch_movie_details_async(session, m) for m in batch_candidates]
                detailed_results = await asyncio.gather(*detail_tasks)
                
                valid_results = [r for r in detailed_results if r is not None]
                
                self._bulk_save(valid_results)
                
    def _bulk_save(self, valid_results: List[Dict]):
        if not valid_results:
            return

        with self.Session() as db_session:
            movie_objects = []
            for data in valid_results:
                movie_objects.append(self.process_movie_data(data))
                self.processed_movies.add(data['basic_data']['id'])
            
            try:
                for movie in movie_objects:
                    db_session.merge(movie)
                db_session.commit()
                logger.info(f"Saved {len(movie_objects)} movies to database.")
            except Exception as e:
                logger.error(f"Database error: {e}")
                db_session.rollback()

    def populate(self, target_size: int = 5000):
        asyncio.run(self.run_population_async(target_size))

if __name__ == "__main__":
    builder = CineCompassDatabaseBuilder()
    builder.populate(target_size=5000)