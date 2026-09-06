"""
Exoplanet Atlas Data Acquisition & Processing Pipeline.

Stage 1 package for ingesting and processing data from the NASA Exoplanet Archive.
"""
from __future__ import annotations

from .config import (
    DEFAULT_TABLE,
    NASA_TAP_URL,
    PROCESSED_METADATA_FILE,
    PROCESSED_PLANETS_FILE,
    RAW_CSV_FILE,
)
from .pipeline import run_pipeline
from .processing import clean_dataframe, save_processed
from .schema import SCHEMA, ColumnSpec, get_schema_names
from .tap_client import TAPError, build_query, fetch_raw_data, query_to_dataframe

__all__ = [
    "run_pipeline",
    "fetch_raw_data",
    "query_to_dataframe",
    "build_query",
    "clean_dataframe",
    "save_processed",
    "TAPError",
    "SCHEMA",
    "ColumnSpec",
    "get_schema_names",
    "NASA_TAP_URL",
    "DEFAULT_TABLE",
    "RAW_CSV_FILE",
    "PROCESSED_PLANETS_FILE",
    "PROCESSED_METADATA_FILE",
]

