"""
Exoplanet Atlas REST API application entrypoint.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.router import api_v1_router
from src.core.config import settings
from src.db.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("exoplanet_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for initialization and teardown."""
    logger.info("Initializing Exoplanet Atlas API...")
    init_db()
    yield
    logger.info("Exoplanet Atlas API shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Service health check endpoint."""
    return {"status": "HEALTHY"}


@app.get("/", tags=["Root"], summary="Root Status")
def root():
    """Root info endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_STR,
    }

