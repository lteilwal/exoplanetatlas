"""
Pydantic schemas for Planetary System entities.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.planet import PlanetSummary
    from src.schemas.star import StarSummary


class SystemBase(BaseModel):
    """Base fields for System."""
    name: str = Field(..., description="Canonical system identifier")

    # Coordinates & Kinematics
    ra: Optional[float] = Field(None, description="Right Ascension (deg)")
    dec: Optional[float] = Field(None, description="Declination (deg)")
    distance_pc: Optional[float] = Field(None, description="Distance from Earth (pc)")
    parallax_mas: Optional[float] = Field(None, description="Trigonometric parallax (mas)")
    proper_motion_mas_yr: Optional[float] = Field(None, description="Proper motion (mas/yr)")
    proper_motion_ra: Optional[float] = Field(None, description="Proper motion in RA (mas/yr)")
    proper_motion_dec: Optional[float] = Field(None, description="Proper motion in Dec (mas/yr)")

    # Architecture & Counts
    star_count: Optional[int] = Field(1, description="Number of stars")
    planet_count: Optional[int] = Field(1, description="Number of confirmed planets")
    moon_count: Optional[int] = Field(0, description="Number of confirmed moons")
    is_circumbinary: Optional[bool] = Field(False, description="Circumbinary flag")

    # Multi-band Photometry
    v_mag: Optional[float] = Field(None, description="Johnson V magnitude")
    b_mag: Optional[float] = Field(None, description="Johnson B magnitude")
    j_mag: Optional[float] = Field(None, description="2MASS J magnitude")
    h_mag: Optional[float] = Field(None, description="2MASS H magnitude")
    k_mag: Optional[float] = Field(None, description="2MASS Ks magnitude")
    gaia_mag: Optional[float] = Field(None, description="Gaia G magnitude")
    tess_mag: Optional[float] = Field(None, description="TESS magnitude")
    kepler_mag: Optional[float] = Field(None, description="Kepler magnitude")


class SystemSummary(SystemBase):
    """Concise system representation for list views and nested references."""
    model_config = ConfigDict(from_attributes=True)

    id: int


class SystemDetail(SystemBase):
    """Full detail view of a system with all its stars and orbiting planets."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    stars: List["StarSummary"] = []
    planets: List["PlanetSummary"] = []

