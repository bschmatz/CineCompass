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
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)