from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints
import uvicorn
from app.database.database_builder import CineCompassDatabaseBuilder
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def populate_database_background(builder: CineCompassDatabaseBuilder):
    try:
        target_size = 5000
        builder.populate_database(target_size=target_size)
        logger.info(f"Database population completed. Target size: {target_size}")
    except Exception as e:
        logger.error(f"Error during background database population: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        builder = CineCompassDatabaseBuilder()
        loop = asyncio.get_event_loop()
        loop.create_task(populate_database_background(builder))
        logger.info("Database population initiated in background")
    except Exception as e:
        logger.error(f"Error during startup database population: {str(e)}")

    yield
    logger.info("Shutting down application")


app = FastAPI(title="CineCompass API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # todo replace with app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)