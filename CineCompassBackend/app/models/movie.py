from CineCompassBackend.app.database.init_db import Base
from sqlalchemy import Column, Integer, String, Float, JSON, Text, DateTime

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    overview = Column(Text)
    genres = Column(JSON)
    cast = Column(JSON)
    director = Column(String)
    popularity = Column(Float)
    vote_average = Column(Float)
    last_updated = Column(DateTime)
    combined_features = Column(Text)
    poster_path = Column(String)  # Store the poster path from TMDB
    backdrop_path = Column(String)  # Store the backdrop path from TMDB

    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def backdrop_url(self):
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/original{self.backdrop_path}"
        return None