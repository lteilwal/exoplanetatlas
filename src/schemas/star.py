"""
Pydantic schemas for Host Star entities.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.planet import PlanetSummary


class StarBase(BaseModel):
    """Base fields for Star."""
    name: str = Field(..., description="Canonical host star name")
    spectral_type: Optional[str] = Field(None, description="MK Spectral type")
    effective_temp_k: Optional[float] = Field(None, description="Effective temperature (K)")
    radius_solar: Optional[float] = Field(None, description="Radius (R_Sun)")
    mass_solar: Optional[float] = Field(None, description="Mass (M_Sun)")
    metallicity_dex: Optional[float] = Field(None, description="Metallicity [Fe/H] (dex)")
    surface_gravity_logg: Optional[float] = Field(None, description="log(g) surface gravity (cgs)")
    luminosity_log_solar: Optional[float] = Field(None, description="log10(L_Sun)")
    age_gyr: Optional[float] = Field(None, description="Age (Gyr)")
    density_g_cm3: Optional[float] = Field(None, description="Density (g/cm³)")
    rotation_period_days: Optional[float] = Field(None, description="Rotation period (days)")
    v_sin_i_km_s: Optional[float] = Field(None, description="Projected rotational velocity (km/s)")
    radial_velocity_km_s: Optional[float] = Field(None, description="Radial velocity (km/s)")
    hd_id: Optional[str] = Field(None, description="HD catalog identifier")
    hip_id: Optional[str] = Field(None, description="Hipparcos identifier")
    tic_id: Optional[str] = Field(None, description="TESS Input Catalog ID")
    gaia_dr2_id: Optional[str] = Field(None, description="Gaia DR2 ID")
    gaia_dr3_id: Optional[str] = Field(None, description="Gaia DR3 ID")


class StarSummary(StarBase):
    """Concise star schema for lists and embedded views."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int


class StarDetail(StarBase):
    """Full detail star view including orbiting planets."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int
    created_at: datetime
    updated_at: datetime
    planets: List["PlanetSummary"] = []

