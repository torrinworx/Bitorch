import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api import router as api_router
from utils.tasks import StartupTasks

load_dotenv()

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await StartupTasks.run()
    yield
    # Shutdown logic here

app = FastAPI(
    title="Bitorch",
    description="""
    """,
    summary="Backend server documentation for Bitorch",
    version="1.0.0",
    lifespan=app_lifespan
)

# CORS configuration
ORIGINS = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Configure the logging format and level
logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO # TODO: Set based on the env: development/deployment or whatever, maybe even a logging env var to set the logging level.
)
