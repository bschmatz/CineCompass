from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.init_db import Base
from passlib.hash import bcrypt

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    last_session_refresh = Column(DateTime, nullable=True)
    ratings = relationship("Rating", back_populates="user")

    @property
    def has_finished_onboarding(self) -> bool:
        return len(self.ratings) > 5

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)