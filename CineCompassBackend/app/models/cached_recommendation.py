from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime
from CineCompassBackend.app.database.init_db import Base
from datetime import datetime


class CachedRecommendation(Base):
    __tablename__ = 'cached_recommendations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    similarity_score = Column(Float)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)