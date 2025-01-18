from sqlalchemy import Column, Integer, String, Boolean
from CineCompassBackend.app.database.init_db import Base
from passlib.hash import bcrypt


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)
