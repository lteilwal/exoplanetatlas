"""
Exoplanet Atlas catalog statistics endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.schemas import StatsResponse
from src.services.system_service import get_aggregate_stats

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("", response_model=StatsResponse, summary="Get catalog aggregate metrics")
def get_stats(
    db: Session = Depends(get_db),
):
    """
    Retrieve comprehensive aggregate metrics, class distributions,
    habitability counts, detection methods, and discovery timeline.
    """
    return get_aggregate_stats(db=db)

