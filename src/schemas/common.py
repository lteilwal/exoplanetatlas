"""
Common Pydantic models for API responses, pagination, and sorting.
"""
from __future__ import annotations

from typing import Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard generic envelope for paginated list responses."""
    model_config = ConfigDict(from_attributes=True)

    items: List[T] = Field(..., description="List of items for the current page")
    total: int = Field(..., description="Total number of items matching filter criteria")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of available pages")


class StatsResponse(BaseModel):
    """Overall dataset summary statistics."""
    total_planets: int
    total_systems: int
    total_stars: int
    multi_planet_systems: int
    planet_class_distribution: dict[str, int]
    habitability_zone_distribution: dict[str, int]
    discovery_method_distribution: dict[str, int]
    discovery_timeline: dict[int, int]

