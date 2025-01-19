from app.database.init_db import Base
from sqlalchemy import Column, Integer, String, Float, JSON, Text, DateTime
from sqlalchemy.orm import relationship


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
    poster_path = Column(String)
    backdrop_path = Column(String)
    ratings = relationship("Rating", back_populates="movie")

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