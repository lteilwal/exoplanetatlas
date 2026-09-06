"""
Aggregated API v1 Router.
"""
from fastapi import APIRouter

from src.api.v1.ai import router as ai_router
from src.api.v1.planets import router as planets_router
from src.api.v1.stars import router as stars_router
from src.api.v1.stats import router as stats_router
from src.api.v1.systems import router as systems_router

api_v1_router = APIRouter()

api_v1_router.include_router(planets_router)
api_v1_router.include_router(systems_router)
api_v1_router.include_router(stars_router)
api_v1_router.include_router(stats_router)
api_v1_router.include_router(ai_router)
