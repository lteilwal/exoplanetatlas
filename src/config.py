"""
Configuration constants for the Exoplanet Atlas data acquisition pipeline.

Table: `pscomppars` (Planetary Systems Composite Parameters)
Source: https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
DOCS_DIR: Path = PROJECT_ROOT / "docs"

# Target Data Files
RAW_CSV_FILE: Path = RAW_DATA_DIR / "exoplanets_raw.csv"
PROCESSED_PLANETS_FILE: Path = PROCESSED_DATA_DIR / "exoplanets_processed.csv"
PROCESSED_METADATA_FILE: Path = PROCESSED_DATA_DIR / "exoplanets_metadata.json"
DATA_DICTIONARY_FILE: Path = PROCESSED_DATA_DIR / "data_dictionary.json"
LOG_FILE: Path = LOGS_DIR / "exoplanet_pipeline.log"

# TAP Service Configuration
NASA_TAP_URL: str = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
DEFAULT_TABLE: str = "pscomppars" # 1 composite row per confirmed planet

# HTTP User-Agent for polite API requests
HTTP_USER_AGENT: str = "ExoplanetAtlas-Pipeline/1.0 (NASA-TAP-Client)"

# HTTP Settings
HTTP_TIMEOUT_SECONDS: int = 120
HTTP_RETRIES: int = 3
HTTP_BACKOFF_SECONDS: float = 3.0

# Logging Configuration
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# Full table query (all 700+ raw columns)
DEFAULT_FULL_QUERY: str = f"SELECT * FROM {DEFAULT_TABLE} ORDER BY pl_name"

# Table default query
DEFAULT_QUERY: str = DEFAULT_FULL_QUERY


def ensure_directories() -> None:
    """Create data, logs, and docs directories on disk if not already present."""
    for directory in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR, DOCS_DIR):
        directory.mkdir(parents=True, exist_ok=True)