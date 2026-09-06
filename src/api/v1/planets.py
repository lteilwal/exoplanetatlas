"""
Planets REST API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.core.config import settings
from src.schemas import PaginatedResponse, PlanetDetail, PlanetSummary
from src.services.planet_service import get_planet_by_id_or_name, get_planets

router = APIRouter(prefix="/planets", tags=["Planets"])


@router.get("", response_model=PaginatedResponse[PlanetSummary], summary="List and filter exoplanets")
def list_planets(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Items per page"),
    search: Optional[str] = Query(None, description="Search text across planet, system, and star names"),
    planet_class: Optional[str] = Query(None, description="Planet classification (Terrestrial, Super-Earth, etc.)"),
    habitability_zone_est: Optional[str] = Query(None, description="Habitability regime"),
    discovery_method: Optional[str] = Query(None, description="Detection method (Transit, Radial Velocity, etc.)"),
    discovery_year: Optional[int] = Query(None, description="Discovery year"),
    discovery_facility: Optional[str] = Query(None, description="Observatory / Facility"),
    min_radius_earth: Optional[float] = Query(None, description="Minimum radius in Earth radii"),
    max_radius_earth: Optional[float] = Query(None, description="Maximum radius in Earth radii"),
    min_mass_earth: Optional[float] = Query(None, description="Minimum mass in Earth masses"),
    max_mass_earth: Optional[float] = Query(None, description="Maximum mass in Earth masses"),
    min_period_days: Optional[float] = Query(None, description="Minimum orbital period in days"),
    max_period_days: Optional[float] = Query(None, description="Maximum orbital period in days"),
    min_equilibrium_temp_k: Optional[float] = Query(None, description="Minimum equilibrium temperature in Kelvin"),
    max_equilibrium_temp_k: Optional[float] = Query(None, description="Maximum equilibrium temperature in Kelvin"),
    min_distance_pc: Optional[float] = Query(None, description="Minimum distance from Earth in parsecs"),
    max_distance_pc: Optional[float] = Query(None, description="Maximum distance from Earth in parsecs"),
    system_name: Optional[str] = Query(None, description="Host system name filter"),
    star_name: Optional[str] = Query(None, description="Host star name filter"),
    sort_by: str = Query("name", description="Sort field: name, period, radius, mass, temp, distance, year"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated, filterable, and sortable collection of confirmed exoplanets.
    """
    items, total_items, total_pages = get_planets(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        planet_class=planet_class,
        habitability_zone_est=habitability_zone_est,
        discovery_method=discovery_method,
        discovery_year=discovery_year,
        discovery_facility=discovery_facility,
        min_radius_earth=min_radius_earth,
        max_radius_earth=max_radius_earth,
        min_mass_earth=min_mass_earth,
        max_mass_earth=max_mass_earth,
        min_period_days=min_period_days,
        max_period_days=max_period_days,
        min_equilibrium_temp_k=min_equilibrium_temp_k,
        max_equilibrium_temp_k=max_equilibrium_temp_k,
        min_distance_pc=min_distance_pc,
        max_distance_pc=max_distance_pc,
        system_name=system_name,
        star_name=star_name,
        sort_by=sort_by,
        order=order,
    )

    return PaginatedResponse[PlanetSummary](
        items=items,
        total=total_items,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{id_or_name}", response_model=PlanetDetail, summary="Get individual planet details")
def get_planet(
    id_or_name: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve full details for a single planet by integer ID or unique name.
    Includes nested relations for host star, system, and discovery records.
    """
    planet = get_planet_by_id_or_name(db=db, identifier=id_or_name)
    if not planet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planet '{id_or_name}' not found.",
        )
    return planet
