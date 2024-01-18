import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from backend.api import router as api_router
from utils.tasks import StartupTasks
from utils.scheduler import scheduler
import utils.mongo as mongo

from middleware import setup_middlewares

load_dotenv()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await StartupTasks.run()
    scheduler.run()

    yield

    scheduler.shutdown()
    await mongo.mongo_manager.close_connection()


app = FastAPI(
    title="Bitorch",
    description="""
    """,
    summary="Backend server documentation for Bitorch",
    version="1.0.0",
    lifespan=app_lifespan,
)

setup_middlewares(app)

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
    level=logging.INFO,  # TODO: Set based on the env: development/deployment or whatever, maybe even a logging env var to set the logging level.
)
