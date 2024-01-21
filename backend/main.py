import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import utils.mongo as mongo
from utils.utils import Utils
from utils.tasks import StartupTasks
from utils.scheduler import scheduler
from middleware import setup_middlewares
from backend.api import router as api_router
from utils.mongo import test_mongo_operations

load_dotenv()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await StartupTasks.run()
    scheduler.run()

    if Utils.env == "development":
        test_result = await test_mongo_operations()
        print("INFO: Mongo test", "passed" if test_result else "failed")

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