"""
Host Stars REST API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.config import settings
from src.schemas import PaginatedResponse, StarDetail, StarSummary
from src.services.system_service import get_star_by_id_or_name, get_stars

router = APIRouter(prefix="/stars", tags=["Stars"])


@router.get("", response_model=PaginatedResponse[StarSummary], summary="List and filter host stars")
def list_stars(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Items per page"),
    search: Optional[str] = Query(None, description="Search star by name"),
    spectral_type: Optional[str] = Query(None, description="Spectral class filter prefix (e.g. 'M', 'G', 'K')"),
    min_mass_solar: Optional[float] = Query(None, description="Minimum mass in Solar masses"),
    max_mass_solar: Optional[float] = Query(None, description="Maximum mass in Solar masses"),
    min_temp_k: Optional[float] = Query(None, description="Minimum effective temperature in Kelvin"),
    max_temp_k: Optional[float] = Query(None, description="Maximum effective temperature in Kelvin"),
    sort_by: str = Query("name", description="Sort field: name, teff, mass, radius"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated host stars with astrophysical properties.
    """
    items, total_items, total_pages = get_stars(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        spectral_type=spectral_type,
        min_mass_solar=min_mass_solar,
        max_mass_solar=max_mass_solar,
        min_temp_k=min_temp_k,
        max_temp_k=max_temp_k,
        sort_by=sort_by,
        order=order,
    )

    return PaginatedResponse[StarSummary](
        items=items,
        total=total_items,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{id_or_name}", response_model=StarDetail, summary="Get individual star details")
def get_star(
    id_or_name: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve full details for a single host star including all orbiting planets.
    """
    star = get_star_by_id_or_name(db=db, identifier=id_or_name)
    if not star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Star '{id_or_name}' not found.",
        )
    return star
