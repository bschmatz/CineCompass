from sqlalchemy import Column, Integer, Float, DateTime, JSON, ForeignKey, String
from app.database.init_db import Base
from datetime import datetime

class CachedRecommendation(Base):
    __tablename__ = "cached_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    similarity_score = Column(Float)
    details = Column(JSON)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)