"""
Main Pipeline Orchestrator for Exoplanet Atlas.

Coordinates end-to-end data ingestion, validation, astronomical transformation,
and structured persistence:
    1. Query NASA Exoplanet Archive TAP service (synchronous HTTP).
    2. Save raw data archive locally.
    3. Sanitize and validate physical constraints.
    4. Compute derived astronomical classifications (planet class, habitability, density).
    5. Align strictly with the curated 4-domain schema and enforce dtypes.
    6. Persist clean dataset, metadata summary report, and data dictionary.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from . import config
from .processing import clean_dataframe, save_processed
from .tap_client import fetch_raw_data

logger = logging.getLogger("exoplanet_pipeline")


def setup_logging(level: str = config.LOG_LEVEL) -> None:
    """Configure console and file logging."""
    config.ensure_directories()

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers if already configured
    if not root_logger.handlers:
        formatter = logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)

        # File handler
        file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        root_logger.addHandler(console_handler)


def run_pipeline(
    limit: Optional[int] = None, # No. of rows downloaded
    curated_only: bool = True, # NASA's curated "useful" columns
    strict_filters: bool = False, # excludes planets with missing periods or masses
    raw_csv_path: Optional[str | Path] = None,
    processed_csv_path: Optional[str | Path] = None,
    metadata_json_path: Optional[str | Path] = None,
    use_existing_raw: bool = False, # Process local .csv (if exists)
) -> dict[str, Any]:
    """
    Execute the complete data pipeline.

    Parameters
    ----------
    limit : int, optional
        Optional limit on number of rows to retrieve (useful for testing).
    curated_only : bool, default True
        If True, queries the curated schema (~85 columns) for high speed and low bandwidth.
        If False, queries all 703 raw columns from pscomppars.
    strict_filters : bool, default False
        If True, excludes planets with missing periods or masses.
    raw_csv_path : str or Path, optional
        Destination path for raw CSV.
    processed_csv_path : str or Path, optional
        Destination path for cleaned CSV.
    metadata_json_path : str or Path, optional
        Destination path for metadata JSON.
    use_existing_raw : bool, default False
        If True, skips the TAP query and processes an existing raw CSV on disk.

    Returns
    -------
    dict[str, Any]
        Summary report containing dataset statistics (exoplanets_metadata.json) and filepaths.
    """
    # Step 0: Logging setup
    setup_logging()
    total_start = time.time()
    raw_path = Path(raw_csv_path) if raw_csv_path else config.RAW_CSV_FILE
    proc_path = Path(processed_csv_path) if processed_csv_path else config.PROCESSED_PLANETS_FILE
    meta_path = Path(metadata_json_path) if metadata_json_path else config.PROCESSED_METADATA_FILE

    logger.info("=" * 70)
    logger.info("STARTING EXOPLANET ATLAS PIPELINE")
    logger.info("=" * 70)

    # Step 1: Data Ingestion

    if use_existing_raw and raw_path.exists():
        logger.info(f"Step 1: Loading existing raw data from: {raw_path}")
        raw_df = pd.read_csv(raw_path, low_memory=False)
        logger.info(f"Loaded {raw_df.shape[0]} rows x {raw_df.shape[1]} columns from disk")
    else:
        mode_str = f"curated schema (~85 cols)" if curated_only else "full table (703 cols)"
        limit_str = f", limit={limit}" if limit else ""
        logger.info(f"Step 1: Fetching data from NASA TAP service ({mode_str}{limit_str})")

        # tap_client.py called to get data from NASA's Exoplanet Archive
        raw_df = fetch_raw_data(
            output_path=raw_path,
            curated_only=curated_only,
            limit=limit,
        )

    # Step 2: Processing, Validation & Transformation

    logger.info("Step 2: Cleaning, validating, and calculating derived astronomical features")

    # processing.py called to refine data
    processed_df, metadata = clean_dataframe(raw_df, strict_filters=strict_filters)

    # Step 3: Persistence
    logger.info("Step 3: Persisting cleaned dataset, metadata report, and data dictionary")

    # processing.py saves the processed data
    saved_csv, saved_json, saved_dict = save_processed(
        df=processed_df,
        metadata=metadata,
        csv_path=proc_path,
        json_path=meta_path,
        dict_path=config.DATA_DICTIONARY_FILE,
    )

    total_elapsed = time.time() - total_start
    logger.info(f"Pipeline completed successfully in {total_elapsed:.2f}s")
    logger.info("=" * 70)

    # metadata packaged into a dictionary
    return {
        "status": "SUCCESS",
        "input_rows": metadata["input_rows"],
        "output_rows": metadata["output_rows"],
        "columns_count": metadata["columns_count"],
        "unique_host_stars": metadata["unique_host_stars"],
        "multi_planet_systems": metadata["multi_planet_systems"],
        "completeness_overall_pct": metadata["completeness_overall_pct"],
        "raw_csv_path": str(raw_path),
        "processed_csv_path": saved_csv,
        "metadata_json_path": saved_json,
        "data_dictionary_path": saved_dict,
        "total_elapsed_seconds": round(total_elapsed, 2),
    }

# COMMAND LINE INTERFACE
def main() -> None:
    """CLI entry point."""
    # Parser used to add flags/arguments
    parser = argparse.ArgumentParser(
        description="Exoplanet Atlas Pipeline: NASA TAP Data Acquisition & Processing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Query all 700+ raw columns instead of the curated schema (~85 columns)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of rows to retrieve (e.g. 100 for testing)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Apply strict filtering (drop planets missing orbital period or mass)",
    )
    parser.add_argument(
        "--from-raw",
        action="store_true",
        default=False,
        help="Skip TAP download and process existing data/raw/exoplanets_raw.csv",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=config.LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    # Takes terminal input and passes it to run_pipeline
    result = run_pipeline(
        limit=args.limit,
        curated_only=not args.full,
        strict_filters=args.strict,
        use_existing_raw=args.from_raw,
    )

    print("\n" + "=" * 60)
    print("EXOPLANET ATLAS : INGESTION & PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Confirmed Exoplanets Ingested : {result['output_rows']}")
    print(f"Unique Host Star Systems     : {result['unique_host_stars']}")
    print(f"Multi-Planet Systems         : {result['multi_planet_systems']}")
    print(f"Dataset Columns              : {result['columns_count']}")
    print(f"Overall Cell Completeness    : {result['completeness_overall_pct']}%")
    print(f"Processed CSV Output         : {result['processed_csv_path']}")
    print(f"Metadata Summary Output      : {result['metadata_json_path']}")
    print(f"Data Dictionary Output       : {result['data_dictionary_path']}")
    print(f"Total Execution Time         : {result['total_elapsed_seconds']} seconds")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()