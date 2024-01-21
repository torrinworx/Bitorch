import logging
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import utils.mongo as mongo
from utils.utils import Utils
from utils.tasks import StartupTasks
from utils.scheduler import scheduler
from api.pex.pex_mongo import PexMongo
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

# NOTE: Attempt at logging request data for rate limitor for each peer:
# @app.exception_handler(StarletteHTTPException)
# async def custom_exception_handler(request: Request, exc: StarletteHTTPException):
#     # Construct the RequestInfo instance
#     request_info = Utils.RequestInfo(
#         timestamp=datetime.utcnow().isoformat(),
#         request_type=request.method,
#         endpoint=request.url.path,
#         response_code=str(exc.status_code),
#     )

#     print(request_info)

#     # Log the request info with PexMongo
#     await PexMongo.update_peer_request_history(
#         client_ip=request.client.host, request_info=request_info
#     )

#     # Return the standard error response
#     return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
