from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.init_db import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_session_refresh = Column(DateTime, nullable=True)
    ratings = relationship("Rating", back_populates="user")

    @property
    def has_finished_onboarding(self) -> bool:
        return len(self.ratings) > 5