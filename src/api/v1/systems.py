"""
Planetary Systems REST API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.config import settings
from src.schemas import PaginatedResponse, SystemDetail, SystemSummary
from src.services.system_service import get_system_by_id_or_name, get_systems

router = APIRouter(prefix="/systems", tags=["Systems"])


@router.get("", response_model=PaginatedResponse[SystemSummary], summary="List and filter planetary systems")
def list_systems(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Items per page"),
    search: Optional[str] = Query(None, description="Search text by system name"),
    min_planets: Optional[int] = Query(None, description="Minimum number of confirmed planets"),
    max_distance_pc: Optional[float] = Query(None, description="Maximum distance from Earth in parsecs"),
    is_circumbinary: Optional[bool] = Query(None, description="Circumbinary filter"),
    sort_by: str = Query("name", description="Sort field: name, distance, planets, stars"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated and filterable planetary systems.
    """
    items, total_items, total_pages = get_systems(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        min_planets=min_planets,
        max_distance_pc=max_distance_pc,
        is_circumbinary=is_circumbinary,
        sort_by=sort_by,
        order=order,
    )

    return PaginatedResponse[SystemSummary](
        items=items,
        total=total_items,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{id_or_name}", response_model=SystemDetail, summary="Get individual system details")
def get_system(
    id_or_name: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve full details of a planetary system with all constituent stars and orbiting planets.
    """
    system = get_system_by_id_or_name(db=db, identifier=id_or_name)
    if not system:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System '{id_or_name}' not found.",
        )
    return system
