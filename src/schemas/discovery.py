"""
Pydantic schemas for Discovery information.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DiscoveryBase(BaseModel):
    """Base fields for Discovery."""
    discovery_method: str = Field(..., description="Detection technique (e.g. Transit, Radial Velocity)")
    discovery_year: Optional[int] = Field(None, description="Year of publication")
    discovery_facility: Optional[str] = Field(None, description="Observatory / Mission facility")
    discovery_instrument: Optional[str] = Field(None, description="Instrument name")
    discovery_locale: Optional[str] = Field(None, description="'Space' or 'Ground'")
    publication_date: Optional[str] = Field(None, description="Publication date (YYYY-MM)")
    reference_name: Optional[str] = Field(None, description="Bibliographic ADS reference")


class DiscoveryRead(DiscoveryBase):
    """Schema for returning Discovery information."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    planet_id: int
    created_at: datetime
    updated_at: datetime

