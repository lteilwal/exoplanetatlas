"""
Pydantic schemas for Exoplanet entities.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.discovery import DiscoveryRead
from src.schemas.star import StarSummary
from src.schemas.system import SystemSummary


class PlanetBase(BaseModel):
    """Core fields for Planet."""
    name: str = Field(..., description="Canonical exoplanet name")
    planet_letter: Optional[str] = Field(None, description="Letter suffix (b, c, d...)")
    is_controversial: bool = Field(False, description="Controversy flag")

    # Orbital Dynamics
    orbital_period_days: Optional[float] = Field(None, description="Orbital period in days")
    semi_major_axis_au: Optional[float] = Field(None, description="Semi-major axis in AU")
    eccentricity: Optional[float] = Field(None, description="Orbital eccentricity")
    inclination_deg: Optional[float] = Field(None, description="Orbital inclination in degrees")
    longitude_periastron_deg: Optional[float] = Field(None, description="Argument of periastron in degrees")
    periastron_passage_days: Optional[float] = Field(None, description="Time of periastron passage (BJD)")

    # Physical Dimensions & Mass
    radius_earth: Optional[float] = Field(None, description="Planet radius in Earth radii")
    radius_jupiter: Optional[float] = Field(None, description="Planet radius in Jupiter radii")
    mass_earth: Optional[float] = Field(None, description="Planet mass in Earth masses")
    mass_jupiter: Optional[float] = Field(None, description="Planet mass in Jupiter masses")
    best_mass_earth: Optional[float] = Field(None, description="Best-estimate mass in Earth masses")
    best_mass_jupiter: Optional[float] = Field(None, description="Best-estimate mass in Jupiter masses")
    mass_provenance: Optional[str] = Field(None, description="Mass provenance ('Mass' or 'Msini')")
    msini_earth: Optional[float] = Field(None, description="Minimum mass M*sin(i) in Earth masses")
    msini_jupiter: Optional[float] = Field(None, description="Minimum mass M*sin(i) in Jupiter masses")
    density_g_cm3: Optional[float] = Field(None, description="Mean bulk density in g/cm³")

    # Thermodynamics & Insolation
    equilibrium_temp_k: Optional[float] = Field(None, description="Equilibrium temperature in Kelvin")
    insolation_earth: Optional[float] = Field(None, description="Stellar insolation flux in Earth units")

    # Transit & Observables
    transit_duration_hours: Optional[float] = Field(None, description="Transit duration in hours")
    transit_depth_percent: Optional[float] = Field(None, description="Transit depth in percent")
    transit_midpoint_days: Optional[float] = Field(None, description="Transit midpoint in BJD")
    impact_parameter: Optional[float] = Field(None, description="Impact parameter b")
    ratio_planet_to_star_radius: Optional[float] = Field(None, description="Rp / R_star ratio")
    radial_velocity_amplitude_m_s: Optional[float] = Field(None, description="RV semi-amplitude K in m/s")

    # Derived Classifications
    planet_class: Optional[str] = Field(None, description="Classification (Terrestrial, Super-Earth, etc.)")
    habitability_zone_est: Optional[str] = Field(None, description="Habitability regime")

    # Detection Flags
    tran_flag: bool = Field(False, description="Transit detection flag")
    rv_flag: bool = Field(False, description="Radial velocity detection flag")
    ttv_flag: bool = Field(False, description="TTV flag")
    ptv_flag: bool = Field(False, description="PTV flag")
    ast_flag: bool = Field(False, description="Astrometry flag")
    micro_flag: bool = Field(False, description="Microlensing flag")
    ima_flag: bool = Field(False, description="Direct imaging flag")


class PlanetSummary(PlanetBase):
    """Concise planet representation for lists and embedded relations."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int
    star_id: Optional[int] = None
    discovery: Optional[DiscoveryRead] = None


class PlanetDetail(PlanetBase):
    """Complete exoplanet view with nested star, system, and discovery records."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int
    star_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    discovery: Optional[DiscoveryRead] = None
    star: Optional[StarSummary] = None
    system: Optional[SystemSummary] = None

