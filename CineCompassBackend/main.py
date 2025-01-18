from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from CineCompassBackend.app.api.v1 import endpoints
import uvicorn

app = FastAPI(title="CineCompass API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #todo replace with app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

# Running
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)