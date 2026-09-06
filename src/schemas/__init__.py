"""Pydantic schemas export for API serialization and documentation."""
from .common import PaginatedResponse, StatsResponse
from .discovery import DiscoveryBase, DiscoveryRead
from .planet import PlanetBase, PlanetDetail, PlanetSummary
from .star import StarBase, StarDetail, StarSummary
from .system import SystemBase, SystemDetail, SystemSummary

# Rebuild models with forward references in full scope
_schema_scope = {
    "DiscoveryRead": DiscoveryRead,
    "StarSummary": StarSummary,
    "StarDetail": StarDetail,
    "SystemSummary": SystemSummary,
    "SystemDetail": SystemDetail,
    "PlanetSummary": PlanetSummary,
    "PlanetDetail": PlanetDetail,
}

PlanetDetail.model_rebuild(_types_namespace=_schema_scope)
StarDetail.model_rebuild(_types_namespace=_schema_scope)
SystemDetail.model_rebuild(_types_namespace=_schema_scope)

__all__ = [
    "PaginatedResponse",
    "StatsResponse",
    "DiscoveryBase",
    "DiscoveryRead",
    "PlanetBase",
    "PlanetSummary",
    "PlanetDetail",
    "StarBase",
    "StarSummary",
    "StarDetail",
    "SystemBase",
    "SystemSummary",
    "SystemDetail",
]

