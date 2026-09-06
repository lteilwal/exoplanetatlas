"""
Planet query and search services with filtering, sorting, and pagination.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from src.models import Discovery, Planet, Star, System


def get_planets(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    search: Optional[str] = None,
    planet_class: Optional[str] = None,
    habitability_zone_est: Optional[str] = None,
    discovery_method: Optional[str] = None,
    discovery_year: Optional[int] = None,
    discovery_facility: Optional[str] = None,
    min_radius_earth: Optional[float] = None,
    max_radius_earth: Optional[float] = None,
    min_mass_earth: Optional[float] = None,
    max_mass_earth: Optional[float] = None,
    min_period_days: Optional[float] = None,
    max_period_days: Optional[float] = None,
    min_equilibrium_temp_k: Optional[float] = None,
    max_equilibrium_temp_k: Optional[float] = None,
    min_distance_pc: Optional[float] = None,
    max_distance_pc: Optional[float] = None,
    system_name: Optional[str] = None,
    star_name: Optional[str] = None,
    sort_by: str = "name",
    order: str = "asc",
) -> Tuple[List[Planet], int, int]:
    """
    Search, filter, sort, and paginate exoplanets.
    Returns: (items, total_count, total_pages)
    """
    query = (
        select(Planet)
        .outerjoin(Planet.discovery)
        .outerjoin(Planet.system)
        .outerjoin(Planet.star)
        .options(
            joinedload(Planet.discovery),
            joinedload(Planet.system),
            joinedload(Planet.star),
        )
    )

    # 1. Text Search across Planet, Star, and System names
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                Planet.name.ilike(search_pattern),
                System.name.ilike(search_pattern),
                Star.name.ilike(search_pattern),
                Discovery.discovery_facility.ilike(search_pattern),
            )
        )

    # 2. Categorical filters
    if planet_class:
        query = query.where(Planet.planet_class == planet_class)
    if habitability_zone_est:
        query = query.where(Planet.habitability_zone_est == habitability_zone_est)
    if discovery_method:
        query = query.where(Discovery.discovery_method.ilike(f"%{discovery_method}%"))
    if discovery_year:
        query = query.where(Discovery.discovery_year == discovery_year)
    if discovery_facility:
        query = query.where(Discovery.discovery_facility.ilike(f"%{discovery_facility}%"))
    if system_name:
        query = query.where(System.name.ilike(f"%{system_name}%"))
    if star_name:
        query = query.where(Star.name.ilike(f"%{star_name}%"))

    # 3. Numeric range filters
    if min_radius_earth is not None:
        query = query.where(Planet.radius_earth >= min_radius_earth)
    if max_radius_earth is not None:
        query = query.where(Planet.radius_earth <= max_radius_earth)

    if min_mass_earth is not None:
        query = query.where(Planet.mass_earth >= min_mass_earth)
    if max_mass_earth is not None:
        query = query.where(Planet.mass_earth <= max_mass_earth)

    if min_period_days is not None:
        query = query.where(Planet.orbital_period_days >= min_period_days)
    if max_period_days is not None:
        query = query.where(Planet.orbital_period_days <= max_period_days)

    if min_equilibrium_temp_k is not None:
        query = query.where(Planet.equilibrium_temp_k >= min_equilibrium_temp_k)
    if max_equilibrium_temp_k is not None:
        query = query.where(Planet.equilibrium_temp_k <= max_equilibrium_temp_k)

    if min_distance_pc is not None:
        query = query.where(System.distance_pc >= min_distance_pc)
    if max_distance_pc is not None:
        query = query.where(System.distance_pc <= max_distance_pc)

    # 4. Total Count calculation
    count_query = select(func.count()).select_from(query.subquery())
    total_items = db.scalar(count_query) or 0

    # 5. Sorting
    sort_column_map = {
        "name": Planet.name,
        "period": Planet.orbital_period_days,
        "radius": Planet.radius_earth,
        "mass": Planet.mass_earth,
        "temp": Planet.equilibrium_temp_k,
        "distance": System.distance_pc,
        "year": Discovery.discovery_year,
    }
    sort_target = sort_column_map.get(sort_by.lower(), Planet.name)

    if order.lower() == "desc":
        query = query.order_by(sort_target.desc().nullslast(), Planet.name.asc())
    else:
        query = query.order_by(sort_target.asc().nullslast(), Planet.name.asc())

    # 6. Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    items = list(db.scalars(query).unique().all())
    total_pages = max(1, math.ceil(total_items / page_size))

    return items, total_items, total_pages


def get_planet_by_id_or_name(db: Session, identifier: str) -> Optional[Planet]:
    """
    Retrieve a single planet by integer ID or unique name.
    """
    query = (
        select(Planet)
        .options(
            joinedload(Planet.discovery),
            joinedload(Planet.system),
            joinedload(Planet.star),
        )
    )

    if identifier.isdigit():
        return db.scalar(query.where(Planet.id == int(identifier)))
    return db.scalar(query.where(Planet.name.ilike(identifier.strip())))

