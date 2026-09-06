"""
AI Service integrating Gemini with Exoplanet Atlas MCP Tools.

Gemini interacts with the verified NASA Exoplanet Archive database strictly
through Model Context Protocol (MCP) tools. The database remains the sole source
of truth for all astronomical measurements.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from google import genai
from google.genai import types

from src.core.config import settings
from src.mcp.server import (
    MCP_TOOL_HANDLERS,
    tool_compare_planets,
    tool_get_planet,
    tool_get_star,
    tool_get_system,
    tool_search_planets,
)

logger = logging.getLogger("exoplanet.ai")

# List of callable MCP tool functions passed to Gemini
MCP_TOOLS = [
    tool_get_planet,
    tool_get_system,
    tool_get_star,
    tool_search_planets,
    tool_compare_planets,
]

DATABASE_SCHEMA_REFERENCE = """DATABASE SEMANTIC SCHEMA REFERENCE:
The database contains 4 normalized relational tables populated from NASA Exoplanet Archive composite parameters:

1. `systems` (Planetary Systems):
   - `name` (str): Unique system designation.
   - `distance_pc` (float, parsecs): Distance from Earth (1 pc ≈ 3.26 light-years). Nullable.
   - `ra` (float, degrees): Right Ascension J2000 celestial coordinate. Nullable.
   - `dec` (float, degrees): Declination J2000 celestial coordinate. Nullable.
   - `star_count` (int): Number of stars in the system (multiplicity).
   - `planet_count` (int): Number of confirmed planets in the system.
   - `is_circumbinary` (bool): True if planet(s) orbit a binary star pair.
   - Multi-band magnitudes: `v_mag`, `gaia_mag`, `tess_mag`, `kepler_mag` (apparent magnitudes; smaller = brighter). Nullable.

2. `stars` (Host Stars):
   - `name` (str): Unique stellar identifier. Belongs to a system (`system_id`).
   - `spectral_type` (str): Morgan-Keenan spectral classification (e.g. 'M1V', 'G2V', 'K5'). Nullable.
   - `effective_temp_k` (float, Kelvin): Photospheric temperature (Sun ≈ 5778 K). Nullable.
   - `mass_solar` (float, M☉): Stellar mass relative to the Sun (1.0 M☉ = 1.989e30 kg). Nullable.
   - `radius_solar` (float, R☉): Stellar radius relative to the Sun (1.0 R☉ = 6.96e5 km). Nullable.
   - `metallicity` (float, dex): Iron abundance relative to hydrogen [Fe/H] (0.0 = solar metallicity). Nullable.

3. `planets` (Confirmed Exoplanets):
   - `name` (str): Unique planetary designation. Belongs to a `system_id` and `star_id`.
   - `orbital_period_days` (float, Earth days): Time for one complete orbit. Nullable.
   - `semi_major_axis_au` (float, AU): Mean orbital distance (1 AU ≈ 1.496e8 km). Nullable.
   - `eccentricity` (float, [0, 1)): Orbital elongation (0 = circular). Nullable.
   - `inclination_deg` (float, degrees): Orbital plane tilt relative to line of sight (90° = edge-on transit). Nullable.
   - `radius_earth` (float, R⊕): Physical radius relative to Earth (1 R⊕ = 6,371 km). Nullable.
   - `radius_jupiter` (float, RJ): Physical radius relative to Jupiter (1 RJ ≈ 11.2 R⊕). Nullable.
   - `mass_earth` (float, M⊕): Mass relative to Earth (1 M⊕ = 5.972e24 kg). Nullable.
   - `mass_jupiter` (float, MJ): Mass relative to Jupiter (1 MJ ≈ 317.8 M⊕). Nullable.
   - `equilibrium_temp_k` (float, Kelvin): Blackbody equilibrium temperature assuming uniform redistribution. Nullable.
   - `insolation_earth` (float, S⊕): Incident stellar flux relative to Earth (1.0 S⊕ = 1361 W/m²). Nullable.

   **CATALOGUED VS DERIVED FIELDS**:
   - *Direct Observational Archive Values*: All fields above except density, class, and habitability zone.
   - *ExoPlanet Atlas Derived Value*: `density_g_cm3` (float, g/cm³): Computed as ρ = 5.515 * (mass_earth / radius_earth^3). Null if mass or radius is missing.
   - *ExoPlanet Atlas Derived Value*: `planet_class` (str): Morphological classification based on radius:
     • Terrestrial (< 1.25 R⊕)
     • Super-Earth (1.25 - 2.0 R⊕)
     • Sub-Neptune (2.0 - 4.0 R⊕)
     • Neptune-like (4.0 - 6.0 R⊕)
     • Gas Giant (≥ 6.0 R⊕)
   - *ExoPlanet Atlas Derived Value*: `habitability_zone_est` (str): Kopparapu stellar insolation model:
     • 'Conservative Habitable Zone' (Runaway Greenhouse to Maximum Greenhouse)
     • 'Optimistic Habitable Zone' (Recent Venus to Early Mars)
     • 'Hot Zone' (inside inner HZ)
     • 'Cold Zone' (outside outer HZ)
     • Null if stellar luminosity/temperature is unavailable.

4. `discoveries` (Discovery Circumstances):
   - `planet_id` (int): 1-to-1 foreign key to `planets.id`.
   - `discovery_method` (str): Primary detection technique (e.g. 'Transit', 'Radial Velocity', 'Microlensing', 'Direct Imaging').
   - `discovery_year` (int): Year confirmed/published.
   - `discovery_facility` (str): Observatory, telescope, or space mission (e.g. 'Kepler', 'TESS', 'W. M. Keck Observatory').

NULLABLE FIELDS MEANING:
Astronomical catalogs are sparse. A null value means the parameter has NOT been measured or is unconstrained by observations (e.g. a planet discovered by Transit often lacks mass unless RV or TTV follow-up was performed). Null does NOT mean zero.
"""

SYSTEM_INSTRUCTION = f"""You are the Exoplanet Atlas Scientific Research Assistant.
You answer astronomical questions strictly based on data retrieved via Model Context Protocol (MCP) tools.

{DATABASE_SCHEMA_REFERENCE}

CORE OPERATIONAL RULES:
1. TOOL USAGE: Always call the appropriate MCP tool (`tool_get_planet`, `tool_get_system`, `tool_get_star`, `tool_search_planets`, `tool_compare_planets`) to obtain database facts before formulating your response.
2. GROUNDING & UNITS: Use the schema reference to correctly interpret property names, numerical units, and physical meanings (e.g., Earth radii vs Jupiter radii, Kelvin, parsecs).
3. NO HALLUCINATIONS / MISSING DATA: NEVER invent, guess, or extrapolate unrecorded measurements or discovery details.
4. DISTINGUISH NO-RESULT VS NULL:
   - Entity Not Found (`found=False`): If a planet, star, or system does not exist in the database, explicitly tell the user that the entity was not found in the catalog and suggest checking the spelling.
   - Value Unavailable (`found=True`, field=null): If an entity exists but a specific property is null, explicitly state: "According to archive records, this property has not been measured or is unconstrained for this object." Never substitute unmeasured values with zero or assumptions.
5. DERIVED VS CATALOGUED DISTINCTION: When discussing density, planet_class, or habitability_zone_est, clearly state that these are derived features calculated by the ExoPlanet Atlas pipeline based on standard astrophysical models (e.g., Kopparapu habitable zone boundaries, radius morphological bins).
6. NO SQL: Never attempt to write, generate, or execute raw SQL queries. All database access must occur solely through the provided MCP tools.
7. TONE: Concise, rigorous, professional, and scientifically precise.
"""


def _get_gemini_client() -> Optional[genai.Client]:
    """Initialize Gemini client if API key is configured."""
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key.strip() in ["", "your_gemini_api_key_here"]:
        return None
    try:
        return genai.Client(api_key=api_key.strip())
    except Exception as e:
        logger.warning("Failed to initialize Gemini client: %s", e)
        return None


def generate_planet_summary_ai(planet_name: str) -> Tuple[str, List[str], List[str]]:
    """
    Generate a factual natural-language summary of a planet using Gemini + MCP tools.
    Returns: (summary_text, bulleted_key_facts, tools_used)
    """
    start_time = time.perf_counter()
    client = _get_gemini_client()
    tools_used = ["tool_get_planet"]

    # 1. If Gemini API is configured, use Gemini with MCP tools
    if client:
        try:
            prompt = (
                f"Please generate a concise, factual scientific summary for the confirmed exoplanet '{planet_name}'. "
                f"Retrieve its data using the `tool_get_planet` tool. Cover its classification, host star, physical scale "
                f"(radius, mass, density), orbital mechanics (period, semi-major axis, eccentricity), thermal regime "
                f"(equilibrium temperature, insolation, habitable zone), and discovery method/year. "
                f"Clearly distinguish catalogued measurements from derived values, and explicitly note any unmeasured properties."
            )
            config = types.GenerateContentConfig(
                tools=MCP_TOOLS,
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            text = response.text or "No text generated."

            # Extract key facts from the structured database record
            data = tool_get_planet(planet_name)
            key_facts = _extract_key_facts(data)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "AI summary generated (Gemini) | planet='%s' | tools=%s | duration_ms=%.2f",
                planet_name,
                tools_used,
                duration_ms,
            )
            return text, key_facts, tools_used
        except Exception as e:
            logger.error(
                "Gemini API error during summary generation | planet='%s' | error=%s",
                planet_name,
                e,
            )
            # Fall back to direct MCP tool formatting below

    # 2. Deterministic Fallback: Format directly from MCP tool data
    data = tool_get_planet(planet_name)
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    if not data.get("found"):
        logger.info(
            "AI summary fallback (Not Found) | planet='%s' | duration_ms=%.2f",
            planet_name,
            duration_ms,
        )
        return (
            f"Exoplanet '{planet_name}' was not found in the database. Please verify the astronomical designation.",
            [],
            tools_used,
        )

    summary = _format_mcp_planet_summary(data)
    key_facts = _extract_key_facts(data)
    logger.info(
        "AI summary generated (MCP Fallback) | planet='%s' | facts_count=%d | duration_ms=%.2f",
        planet_name,
        len(key_facts),
        duration_ms,
    )
    return summary, key_facts, tools_used


def ask_planet_question_ai(planet_name: str, question: str) -> Tuple[str, List[str], List[str]]:
    """
    Answer a question regarding an exoplanet using Gemini + MCP tools.
    Returns: (answer_text, tools_used, fields_referenced)
    """
    start_time = time.perf_counter()
    client = _get_gemini_client()
    tools_used = ["tool_get_planet"]
    fields_referenced: List[str] = []

    # 1. If Gemini API is configured, execute query with MCP tools
    if client:
        try:
            prompt = (
                f"Target planet: '{planet_name}'.\n"
                f"User Question: '{question}'.\n"
                f"Use the `tool_get_planet` tool (and `tool_get_star` or `tool_get_system` if relevant) to retrieve "
                f"the factual data. Answer strictly based on the database information. If the requested information "
                f"is not recorded or null in the database, explicitly state that it has not been measured. "
                f"If the planet itself is not found, state that it does not exist in the database."
            )
            config = types.GenerateContentConfig(
                tools=MCP_TOOLS,
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,
            )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            text = response.text or "No answer returned by Gemini."
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "AI Q&A answered (Gemini) | planet='%s' | question='%s' | duration_ms=%.2f",
                planet_name,
                question[:50],
                duration_ms,
            )
            return text, tools_used, ["mcp.tool_get_planet"]
        except Exception as e:
            logger.error(
                "Gemini API error during Q&A | planet='%s' | error=%s",
                planet_name,
                e,
            )

    # 2. Deterministic Fallback: Answer directly from MCP tool properties
    data = tool_get_planet(planet_name)
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    if not data.get("found"):
        logger.info(
            "AI Q&A fallback (Not Found) | planet='%s' | duration_ms=%.2f",
            planet_name,
            duration_ms,
        )
        return (
            f"Exoplanet '{planet_name}' is not recorded in the database. Please check the spelling or designation.",
            tools_used,
            [],
        )

    answer, fields_referenced = _answer_from_mcp_data(data, question)
    logger.info(
        "AI Q&A answered (MCP Fallback) | planet='%s' | fields=%s | duration_ms=%.2f",
        planet_name,
        fields_referenced,
        duration_ms,
    )
    return answer, tools_used, fields_referenced


def general_chat_ai(message: str, context_planet: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    General conversational endpoint powered by Gemini with full access to MCP tools.
    """
    start_time = time.perf_counter()
    client = _get_gemini_client()
    tools_used = ["mcp_tools"]

    if client:
        try:
            context_prefix = f"Active planet context: {context_planet}\n" if context_planet else ""
            prompt = f"{context_prefix}User Inquiry: {message}"
            config = types.GenerateContentConfig(
                tools=MCP_TOOLS,
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                "AI chat completed (Gemini) | query='%s' | duration_ms=%.2f",
                message[:50],
                duration_ms,
            )
            return response.text or "No response generated.", tools_used
        except Exception as e:
            logger.error("Gemini chat error | query='%s' | error=%s", message[:50], e)
            return f"Gemini connection error: {e}", tools_used

    # Offline search tool fallback
    search_res = tool_search_planets(query=message[:30], limit=5)
    matches = search_res.get("planets", [])
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    if matches:
        names = ", ".join([p.get("name", "Unknown") for p in matches])
        logger.info(
            "AI chat search fallback | query='%s' | matches=%d | duration_ms=%.2f",
            message[:30],
            len(matches),
            duration_ms,
        )
        return (
            f"Database matches for your inquiry: {names}. "
            f"(Configure GEMINI_API_KEY in .env for full Gemini natural language reasoning).",
            ["tool_search_planets"],
        )

    logger.info(
        "AI chat fallback ready | query='%s' | duration_ms=%.2f",
        message[:30],
        duration_ms,
    )
    return (
        "The Exoplanet Atlas MCP tools are ready. Add your GEMINI_API_KEY in .env to enable full Gemini conversation.",
        tools_used,
    )


# ============================================================================
# Helpers for Deterministic Fallbacks and Key Fact Extraction
# ============================================================================

def _extract_key_facts(data: Dict[str, Any]) -> List[str]:
    """Extract bulleted key facts from MCP planet dictionary."""
    facts = []
    if data.get("planet_class"):
        facts.append(f"Class (Derived): {data['planet_class']}")
    if data.get("radius_earth") is not None:
        facts.append(f"Radius: {data['radius_earth']:.2f} R⊕")
    if data.get("mass_earth") is not None:
        facts.append(f"Mass: {data['mass_earth']:.2f} M⊕")
    if data.get("density_g_cm3") is not None:
        facts.append(f"Density (Derived): {data['density_g_cm3']:.2f} g/cm³")
    if data.get("orbital_period_days") is not None:
        facts.append(f"Period: {data['orbital_period_days']:.2f} days")
    if data.get("equilibrium_temp_k") is not None:
        facts.append(f"Equilibrium Temp: {round(data['equilibrium_temp_k'])} K")
    if data.get("habitability_zone_est"):
        facts.append(f"Habitability Zone (Derived): {data['habitability_zone_est']}")
    disc = data.get("discovery") or {}
    if disc.get("discovery_method") and disc.get("discovery_year"):
        facts.append(f"Discovery: {disc['discovery_year']} via {disc['discovery_method']}")
    return facts


def _format_mcp_planet_summary(data: Dict[str, Any]) -> str:
    """Format structured MCP planet data into clean scientific text."""
    name = data.get("name", "Unknown Planet")
    p_class = data.get("planet_class", "unclassified planet")
    star = data.get("star") or {}
    star_name = star.get("name")
    spectral = star.get("spectral_type")
    system = data.get("system") or {}
    distance_pc = system.get("distance_pc")

    radius_e = data.get("radius_earth")
    mass_e = data.get("mass_earth")
    density = data.get("density_g_cm3")
    period = data.get("orbital_period_days")
    sma = data.get("semi_major_axis_au")
    ecc = data.get("eccentricity")
    temp_k = data.get("equilibrium_temp_k")
    hz = data.get("habitability_zone_est")
    disc = data.get("discovery") or {}

    s1 = f"{name} is a confirmed {p_class}"
    if star_name:
        spec_text = f" ({spectral}-type)" if spectral else ""
        s1 += f" orbiting the host star {star_name}{spec_text}"
    if distance_pc is not None:
        dist_ly = distance_pc * 3.26156
        s1 += f" located approximately {distance_pc:.1f} parsecs ({dist_ly:.1f} light-years) from Earth."
    else:
        s1 += "."

    s2_parts = []
    if radius_e is not None:
        s2_parts.append(f"radius of {radius_e:.2f} R⊕")
    if mass_e is not None:
        s2_parts.append(f"mass of {mass_e:.2f} M⊕")
    if density is not None:
        s2_parts.append(f"derived bulk density of {density:.2f} g/cm³")
    s2 = f" It has a measured {', '.join(s2_parts)}." if s2_parts else " Physical scale (radius and mass) is unconstrained in archive records."

    s3_parts = []
    if period is not None:
        s3_parts.append(f"orbital period of {period:.2f} Earth days")
    if sma is not None:
        s3_parts.append(f"semi-major axis of {sma:.4f} AU")
    if ecc is not None and ecc > 0.001:
        s3_parts.append(f"eccentricity of {ecc:.3f}")
    s3 = f" The planet completes its orbit with an {', '.join(s3_parts)}." if s3_parts else ""

    s4 = ""
    if temp_k is not None:
        temp_c = round(temp_k - 273.15)
        s4 += f" Its equilibrium temperature is calculated at {round(temp_k)} K ({temp_c} °C)"
        if hz:
            s4 += f", placing it in the derived {hz}."
        else:
            s4 += "."

    s5 = ""
    if disc.get("discovery_method"):
        s5 = f" Discovered via {disc['discovery_method']}"
        if disc.get("discovery_year"):
            s5 += f" in {disc['discovery_year']}"
        if disc.get("discovery_facility"):
            s5 += f" using {disc['discovery_facility']}."
        else:
            s5 += "."

    return (s1 + s2 + s3 + s4 + s5).strip()


def _answer_from_mcp_data(data: Dict[str, Any], question: str) -> Tuple[str, List[str]]:
    """Grounded fallback Q&A resolver using MCP tool dictionary."""
    q = question.lower()
    name = data.get("name", "This planet")
    fields = []

    if any(k in q for k in ["mass", "heavy", "weight"]):
        mass_e = data.get("mass_earth")
        mass_j = data.get("mass_jupiter")
        if mass_e is not None:
            fields.extend(["mass_earth", "mass_jupiter"])
            mass_j_str = f" ({mass_j:.3f} Jupiter masses)" if mass_j is not None else f" ({mass_e / 317.828:.3f} Jupiter masses)"
            return f"{name} has a recorded mass of {mass_e:.2f} Earth masses{mass_j_str}.", fields
        return f"According to database records retrieved via MCP, the mass of {name} has not been measured or is unconstrained.", fields

    if any(k in q for k in ["radius", "size", "diameter", "big", "large", "dimension"]):
        radius_e = data.get("radius_earth")
        if radius_e is not None:
            fields.append("radius_earth")
            return f"{name} has a measured radius of {radius_e:.2f} Earth radii.", fields
        return f"According to database records, the physical radius of {name} is unmeasured.", fields

    if any(k in q for k in ["density", "composition"]):
        density = data.get("density_g_cm3")
        if density is not None:
            fields.append("density_g_cm3")
            return f"{name} has an ExoPlanet Atlas-derived mean bulk density of {density:.2f} g/cm³ (calculated from measured mass and radius).", fields
        return f"The bulk density for {name} cannot be derived because either mass or radius is unmeasured.", fields

    if any(k in q for k in ["temperature", "temp", "hot", "cold", "climate", "kelvin"]):
        temp_k = data.get("equilibrium_temp_k")
        if temp_k is not None:
            fields.append("equilibrium_temp_k")
            return f"The estimated planetary equilibrium temperature of {name} is {round(temp_k)} K ({round(temp_k - 273.15)} °C).", fields
        return f"The equilibrium temperature of {name} is not recorded in the database.", fields

    if any(k in q for k in ["habitable", "habitability", "life", "water", "goldilocks"]):
        hz = data.get("habitability_zone_est")
        fields.append("habitability_zone_est")
        if hz:
            return f"{name} is classified in the derived '{hz}' regime based on the ExoPlanet Atlas Kopparapu stellar insolation model.", fields
        return f"Habitability classification for {name} is unassigned in current records due to unconstrained stellar flux.", fields

    if any(k in q for k in ["discover", "found", "telescope", "mission", "facility", "how was", "when was"]):
        disc = data.get("discovery") or {}
        fields.extend(["discovery.discovery_method", "discovery.discovery_year"])
        if disc.get("discovery_method") or disc.get("discovery_year"):
            return f"{name} was discovered in {disc.get('discovery_year', 'N/A')} via the {disc.get('discovery_method', 'N/A')} method by {disc.get('discovery_facility', 'archive surveys')}.", fields
        return f"Discovery circumstances for {name} are unrecorded in the database.", fields

    # Default fallback
    return _format_mcp_planet_summary(data), ["dossier"]
