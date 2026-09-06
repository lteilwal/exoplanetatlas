"""
Model Context Protocol (MCP) Server for Exoplanet Atlas.

Exposes thin, controlled, read-only scientific tools that query the PostgreSQL / SQLite
database through existing SQLAlchemy service layers. Gemini calls these tools
to retrieve verified astronomical data.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from mcp.server.mcpserver import MCPServer
from sqlalchemy.orm import Session

import src.db.session as db_session
from src.schemas.planet import PlanetDetail, PlanetSummary
from src.schemas.star import StarDetail
from src.schemas.system import SystemDetail
from src.services.planet_service import get_planet_by_id_or_name, get_planets
from src.services.system_service import (
    get_star_by_id_or_name,
    get_system_by_id_or_name,
)

logger = logging.getLogger("exoplanet.mcp")

# Initialize MCP Server instance
mcp_server = MCPServer("exoplanet-atlas")


# ============================================================================
# Core Tool Implementations (Reusable in-process & via MCP Transport)
# ============================================================================

def tool_get_planet(name: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive scientific dossier for a specific exoplanet by name.

    Args:
        name (str): Full or partial astronomical designation of the planet
                    (e.g., 'TRAPPIST-1 e', 'Kepler-186 f', 'Proxima Centauri b').

    Returns:
        Dict[str, Any]:
            - If found (`found: True`): Complete planetary parameters including
              dimensions (radius_earth, mass_earth, density_g_cm3), orbital ephemeris
              (orbital_period_days, semi_major_axis_au, eccentricity, inclination_deg),
              thermal regime (equilibrium_temp_k, insolation_earth), derived features
              (planet_class, habitability_zone_est), and nested 'star', 'system',
              and 'discovery' objects. Missing/unmeasured parameters are null.
            - If not found (`found: False`): {"found": False, "name": name, "message": "..."}.
    """
    start_time = time.perf_counter()
    db: Session = db_session.SessionLocal()
    try:
        planet = get_planet_by_id_or_name(db, name)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        if not planet:
            logger.info(
                "MCP tool: get_planet | name='%s' | found=False | duration_ms=%.2f",
                name,
                duration_ms,
            )
            return {
                "found": False,
                "name": name,
                "message": f"Exoplanet '{name}' was not found in the database.",
            }

        dto = PlanetDetail.model_validate(planet)
        data = dto.model_dump(mode="json")
        data["found"] = True

        logger.info(
            "MCP tool: get_planet | name='%s' | found=True | id=%s | duration_ms=%.2f",
            name,
            data.get("id"),
            duration_ms,
        )
        return data
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(
            "MCP tool error: get_planet | name='%s' | error=%s | duration_ms=%.2f",
            name,
            e,
            duration_ms,
        )
        raise
    finally:
        db.close()


def tool_get_system(name: str) -> Dict[str, Any]:
    """
    Retrieve planetary system details by name.

    Args:
        name (str): Planetary system designation (e.g., 'TRAPPIST-1', 'Kepler-11', 'HD 10180').

    Returns:
        Dict[str, Any]:
            - If found (`found: True`): System parameters including distance_pc,
              celestial coordinates (ra, dec in degrees), stellar multiplicity (star_count),
              confirmed planet count (planet_count), is_circumbinary flag, multi-band
              apparent magnitudes (v_mag, gaia_mag, tess_mag, kepler_mag), and nested
              lists of all associated 'stars' and confirmed sibling 'planets'.
            - If not found (`found: False`): {"found": False, "name": name, "message": "..."}.
    """
    start_time = time.perf_counter()
    db: Session = db_session.SessionLocal()
    try:
        sys = get_system_by_id_or_name(db, name)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        if not sys:
            logger.info(
                "MCP tool: get_system | name='%s' | found=False | duration_ms=%.2f",
                name,
                duration_ms,
            )
            return {
                "found": False,
                "name": name,
                "message": f"Planetary system '{name}' was not found in the database.",
            }

        dto = SystemDetail.model_validate(sys)
        data = dto.model_dump(mode="json")
        data["found"] = True

        logger.info(
            "MCP tool: get_system | name='%s' | found=True | planets=%d | stars=%d | duration_ms=%.2f",
            name,
            len(data.get("planets", [])),
            len(data.get("stars", [])),
            duration_ms,
        )
        return data
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(
            "MCP tool error: get_system | name='%s' | error=%s | duration_ms=%.2f",
            name,
            e,
            duration_ms,
        )
        raise
    finally:
        db.close()


def tool_get_star(name: str) -> Dict[str, Any]:
    """
    Retrieve host star astrophysical properties by name.

    Args:
        name (str): Host star identifier (e.g., 'TRAPPIST-1', 'Kepler-186', 'Sun').

    Returns:
        Dict[str, Any]:
            - If found (`found: True`): Stellar parameters including Morgan-Keenan
              spectral_type, effective_temp_k (Kelvin), mass_solar (M☉), radius_solar (R☉),
              metallicity ([Fe/H] in dex), system_id, and list of all orbiting 'planets'.
            - If not found (`found: False`): {"found": False, "name": name, "message": "..."}.
    """
    start_time = time.perf_counter()
    db: Session = db_session.SessionLocal()
    try:
        star = get_star_by_id_or_name(db, name)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        if not star:
            logger.info(
                "MCP tool: get_star | name='%s' | found=False | duration_ms=%.2f",
                name,
                duration_ms,
            )
            return {
                "found": False,
                "name": name,
                "message": f"Host star '{name}' was not found in the database.",
            }

        dto = StarDetail.model_validate(star)
        data = dto.model_dump(mode="json")
        data["found"] = True

        logger.info(
            "MCP tool: get_star | name='%s' | found=True | orbiting_planets=%d | duration_ms=%.2f",
            name,
            len(data.get("planets", [])),
            duration_ms,
        )
        return data
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(
            "MCP tool error: get_star | name='%s' | error=%s | duration_ms=%.2f",
            name,
            e,
            duration_ms,
        )
        raise
    finally:
        db.close()


def tool_search_planets(
    query: str = "",
    planet_class: Optional[str] = None,
    habitability_zone: Optional[str] = None,
    discovery_method: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Search and filter the exoplanet catalog by name substring, morphological classification,
    habitability regime, or discovery detection method.

    Args:
        query (str, optional): Substring to match across planet, star, or system names. Defaults to "".
        planet_class (str, optional): Filter by morphology: 'Terrestrial', 'Super-Earth',
                                      'Sub-Neptune', 'Neptune-like', or 'Gas Giant'.
        habitability_zone (str, optional): Filter by habitability model: 'Conservative Habitable Zone',
                                           'Optimistic Habitable Zone', 'Hot Zone', or 'Cold Zone'.
        discovery_method (str, optional): Filter by detection technique (e.g. 'Transit', 'Radial Velocity').
        limit (int, optional): Maximum result count to return (1 to 50, default=10).

    Returns:
        Dict[str, Any]:
            - total_matches (int): Total count of matching planets across the entire database.
            - returned_count (int): Number of planet summary objects returned in this page.
            - planets (List[Dict[str, Any]]): List of PlanetSummary objects with basic telemetry.
    """
    start_time = time.perf_counter()
    db: Session = db_session.SessionLocal()
    try:
        safe_limit = max(1, min(limit, 50))
        items, total, _ = get_planets(
            db=db,
            page=1,
            page_size=safe_limit,
            search=query if query and query.strip() else None,
            planet_class=planet_class if planet_class and planet_class.strip() else None,
            habitability_zone_est=habitability_zone if habitability_zone and habitability_zone.strip() else None,
            discovery_method=discovery_method if discovery_method and discovery_method.strip() else None,
        )
        planets_data = [
            PlanetSummary.model_validate(p).model_dump(mode="json")
            for p in items
        ]
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        logger.info(
            "MCP tool: search_planets | query='%s' | class='%s' | hz='%s' | total=%d | returned=%d | duration_ms=%.2f",
            query,
            planet_class,
            habitability_zone,
            total,
            len(planets_data),
            duration_ms,
        )
        return {
            "total_matches": total,
            "returned_count": len(planets_data),
            "planets": planets_data,
        }
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(
            "MCP tool error: search_planets | query='%s' | error=%s | duration_ms=%.2f",
            query,
            e,
            duration_ms,
        )
        raise
    finally:
        db.close()


def tool_compare_planets(planet_names: List[str]) -> Dict[str, Any]:
    """
    Compare multiple exoplanets side-by-side by providing a list of planet designations.

    Args:
        planet_names (List[str]): List of up to 6 planet names to compare
                                 (e.g., ['TRAPPIST-1 e', 'Kepler-186 f', 'Proxima Centauri b']).

    Returns:
        Dict[str, Any]:
            - comparison_count (int): Number of planet entries evaluated.
            - planets (List[Dict[str, Any]]): List of planet objects. Each entry contains
              `found: True` with full planetary properties, or `{"name": name, "found": False}`
              if that specific planet was not found in the database.
    """
    start_time = time.perf_counter()
    db: Session = db_session.SessionLocal()
    try:
        results = []
        for p_name in planet_names[:6]:  # Limit to max 6 planets for comparison
            planet = get_planet_by_id_or_name(db, p_name)
            if planet:
                dto = PlanetDetail.model_validate(planet)
                p_data = dto.model_dump(mode="json")
                p_data["found"] = True
                results.append(p_data)
            else:
                results.append({
                    "name": p_name,
                    "found": False,
                    "message": f"Exoplanet '{p_name}' was not found in the database.",
                })

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            "MCP tool: compare_planets | count=%d | duration_ms=%.2f",
            len(results),
            duration_ms,
        )
        return {
            "comparison_count": len(results),
            "planets": results,
        }
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(
            "MCP tool error: compare_planets | error=%s | duration_ms=%.2f",
            e,
            duration_ms,
        )
        raise
    finally:
        db.close()


# ============================================================================
# Register Tools with MCP Server
# ============================================================================

@mcp_server.tool()
def get_planet(name: str) -> str:
    """Retrieve comprehensive scientific parameters for an exoplanet by name."""
    return json.dumps(tool_get_planet(name))


@mcp_server.tool()
def get_system(name: str) -> str:
    """Retrieve planetary system architecture and stellar multiplicity by name."""
    return json.dumps(tool_get_system(name))


@mcp_server.tool()
def get_star(name: str) -> str:
    """Retrieve host star astrophysical properties and spectral type by name."""
    return json.dumps(tool_get_star(name))


@mcp_server.tool()
def search_planets(
    query: str = "",
    planet_class: Optional[str] = None,
    habitability_zone: Optional[str] = None,
    discovery_method: Optional[str] = None,
    limit: int = 10,
) -> str:
    """Search confirmed exoplanets with optional morphology and habitability filtering."""
    return json.dumps(
        tool_search_planets(
            query=query,
            planet_class=planet_class,
            habitability_zone=habitability_zone,
            discovery_method=discovery_method,
            limit=limit,
        )
    )


@mcp_server.tool()
def compare_planets(planet_names: List[str]) -> str:
    """Compare multiple exoplanets side-by-side by name (up to 6 planets)."""
    return json.dumps(tool_compare_planets(planet_names))


# Map of available tool functions for in-process Gemini tool execution
MCP_TOOL_HANDLERS = {
    "get_planet": tool_get_planet,
    "get_system": tool_get_system,
    "get_star": tool_get_star,
    "search_planets": tool_search_planets,
    "compare_planets": tool_compare_planets,
}


def run_mcp_server() -> None:
    """Run the MCP server via standard stdio transport."""
    mcp_server.run()


if __name__ == "__main__":
    run_mcp_server()
