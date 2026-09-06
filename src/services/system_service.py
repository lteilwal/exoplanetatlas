"""
Planetary System and Host Star query services.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.models import Discovery, Planet, Star, System


def get_systems(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    search: Optional[str] = None,
    min_planets: Optional[int] = None,
    max_distance_pc: Optional[float] = None,
    is_circumbinary: Optional[bool] = None,
    sort_by: str = "name",
    order: str = "asc",
) -> Tuple[List[System], int, int]:
    """
    Search, filter, and paginate Planetary Systems.
    """
    query = select(System)

    if search:
        query = query.where(System.name.ilike(f"%{search.strip()}%"))
    if min_planets is not None:
        query = query.where(System.planet_count >= min_planets)
    if max_distance_pc is not None:
        query = query.where(System.distance_pc <= max_distance_pc)
    if is_circumbinary is not None:
        query = query.where(System.is_circumbinary == is_circumbinary)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_items = db.scalar(count_query) or 0

    # Sort
    sort_map = {
        "name": System.name,
        "distance": System.distance_pc,
        "planets": System.planet_count,
        "stars": System.star_count,
    }
    sort_col = sort_map.get(sort_by.lower(), System.name)
    if order.lower() == "desc":
        query = query.order_by(sort_col.desc().nullslast(), System.name.asc())
    else:
        query = query.order_by(sort_col.asc().nullslast(), System.name.asc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    items = list(db.scalars(query).all())
    total_pages = max(1, math.ceil(total_items / page_size))

    return items, total_items, total_pages


def get_system_by_id_or_name(db: Session, identifier: str) -> Optional[System]:
    """
    Retrieve single system with constituent stars and orbiting planets.
    """
    query = (
        select(System)
        .options(
            selectinload(System.stars),
            selectinload(System.planets).selectinload(Planet.discovery),
        )
    )

    if identifier.isdigit():
        return db.scalar(query.where(System.id == int(identifier)))
    return db.scalar(query.where(System.name.ilike(identifier.strip())))


def get_stars(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    search: Optional[str] = None,
    spectral_type: Optional[str] = None,
    min_mass_solar: Optional[float] = None,
    max_mass_solar: Optional[float] = None,
    min_temp_k: Optional[float] = None,
    max_temp_k: Optional[float] = None,
    sort_by: str = "name",
    order: str = "asc",
) -> Tuple[List[Star], int, int]:
    """
    Search, filter, and paginate Host Stars.
    """
    query = select(Star)

    if search:
        query = query.where(Star.name.ilike(f"%{search.strip()}%"))
    if spectral_type:
        query = query.where(Star.spectral_type.ilike(f"{spectral_type.strip()}%"))
    if min_mass_solar is not None:
        query = query.where(Star.mass_solar >= min_mass_solar)
    if max_mass_solar is not None:
        query = query.where(Star.mass_solar <= max_mass_solar)
    if min_temp_k is not None:
        query = query.where(Star.effective_temp_k >= min_temp_k)
    if max_temp_k is not None:
        query = query.where(Star.effective_temp_k <= max_temp_k)

    count_query = select(func.count()).select_from(query.subquery())
    total_items = db.scalar(count_query) or 0

    sort_map = {
        "name": Star.name,
        "teff": Star.effective_temp_k,
        "mass": Star.mass_solar,
        "radius": Star.radius_solar,
    }
    sort_col = sort_map.get(sort_by.lower(), Star.name)
    if order.lower() == "desc":
        query = query.order_by(sort_col.desc().nullslast(), Star.name.asc())
    else:
        query = query.order_by(sort_col.asc().nullslast(), Star.name.asc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    items = list(db.scalars(query).all())
    total_pages = max(1, math.ceil(total_items / page_size))

    return items, total_items, total_pages


def get_star_by_id_or_name(db: Session, identifier: str) -> Optional[Star]:
    """
    Retrieve single star with orbiting planets.
    """
    query = select(Star).options(
        selectinload(Star.planets).selectinload(Planet.discovery),
        selectinload(Star.system),
    )

    if identifier.isdigit():
        return db.scalar(query.where(Star.id == int(identifier)))
    return db.scalar(query.where(Star.name.ilike(identifier.strip())))


def get_aggregate_stats(db: Session) -> dict:
    """
    Compute aggregate summary statistics for the exoplanet catalog.
    """
    total_planets = db.scalar(select(func.count(Planet.id))) or 0
    total_systems = db.scalar(select(func.count(System.id))) or 0
    total_stars = db.scalar(select(func.count(Star.id))) or 0
    multi_planet_systems = db.scalar(
        select(func.count(System.id)).where(System.planet_count > 1)
    ) or 0

    # Planet class distribution
    class_rows = db.execute(
        select(Planet.planet_class, func.count(Planet.id))
        .where(Planet.planet_class.is_not(None))
        .group_by(Planet.planet_class)
    ).all()
    planet_class_dist = {r[0]: r[1] for r in class_rows}

    # Habitability zone distribution
    hz_rows = db.execute(
        select(Planet.habitability_zone_est, func.count(Planet.id))
        .where(Planet.habitability_zone_est.is_not(None))
        .group_by(Planet.habitability_zone_est)
    ).all()
    hz_dist = {r[0]: r[1] for r in hz_rows}

    # Discovery method distribution
    method_rows = db.execute(
        select(Discovery.discovery_method, func.count(Discovery.id))
        .where(Discovery.discovery_method.is_not(None))
        .group_by(Discovery.discovery_method)
    ).all()
    method_dist = {r[0]: r[1] for r in method_rows}

    # Discovery timeline by year
    year_rows = db.execute(
        select(Discovery.discovery_year, func.count(Discovery.id))
        .where(Discovery.discovery_year.is_not(None))
        .group_by(Discovery.discovery_year)
        .order_by(Discovery.discovery_year.asc())
    ).all()
    timeline = {int(r[0]): r[1] for r in year_rows if r[0] is not None}

    return {
        "total_planets": total_planets,
        "total_systems": total_systems,
        "total_stars": total_stars,
        "multi_planet_systems": multi_planet_systems,
        "planet_class_distribution": planet_class_dist,
        "habitability_zone_distribution": hz_dist,
        "discovery_method_distribution": method_dist,
        "discovery_timeline": timeline,
    }

