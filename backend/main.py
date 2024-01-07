from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import router as api_router

load_dotenv()

app = FastAPI(
    title="Bitorch",
    description="""
    """,
    summary="Backend server documentation for Bitorch",
    version="1.0.0",
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
