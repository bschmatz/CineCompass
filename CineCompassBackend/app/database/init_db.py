import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def init_db():
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        print("Using DATABASE_URL")
    else:
        directory = Path(__file__).parent
        db_path = directory / "movies.db"
        database_url = f"sqlite:///{db_path}"

    engine = create_engine(database_url)
    
    from app.models.user import User
    from app.models.movie import Movie
    from app.models.rating import Rating
    from app.models.cached_recommendation import CachedRecommendation
    from app.models.cached_recommendation import CachedRecommendation
    
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)