from sqlalchemy import Column, Integer, String, Float, JSON, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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