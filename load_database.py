#!/usr/bin/env python
"""
Exoplanet Atlas - Database Schema Setup & Ingestion CLI.

Initializes tables in PostgreSQL (or SQLite fallback) and ingests the cleaned
exoplanet dataset (`data/processed/exoplanets_processed.csv`).

Usage:
    python load_database.py [--csv data/processed/exoplanets_processed.csv] [--batch-size 500]
"""
import argparse
import logging
import sys
from pathlib import Path

from src.core.config import settings
from src.db.session import init_db
from src.services.ingestion import ingest_from_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("load_database")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest Stage 1 cleaned exoplanet data into relational database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(settings.PROCESSED_CSV_PATH),
        help="Path to cleaned dataset CSV",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Batch size for database commits",
    )

    args = parser.parse_args()
    csv_file = Path(args.csv)

    print("\n" + "=" * 65)
    print("EXOPLANET ATLAS: DATABASE SCHEMA SETUP & INGESTION")
    print("=" * 65)
    print(f"Target Database URI : {settings.SQLALCHEMY_DATABASE_URI}")
    print(f"Source Dataset CSV  : {csv_file}")
    print("=" * 65 + "\n")

    if not csv_file.exists():
        logger.error(f"Error: Source CSV not found at {csv_file}.")
        logger.info("Please run 'python run_pipeline.py' first to acquire NASA dataset.")
        return 1

    logger.info("Step 1: Initializing database schema...")
    init_db()

    logger.info("Step 2: Ingesting cleaned exoplanet records...")
    try:
        stats = ingest_from_csv(csv_path=csv_file, batch_size=args.batch_size)
    except Exception as e:
        logger.error(f"Ingestion failed with exception: {e}", exc_info=True)
        return 1

    print("\n" + "=" * 65)
    print("DATABASE INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 65)
    print(f"Total Rows Processed       : {stats['rows_processed']}")
    print(f"Total Systems In Database  : {stats['systems_count']}")
    print(f"Total Stars In Database    : {stats['stars_count']}")
    print(f"Total Planets In Database  : {stats['planets_count']}")
    print(f"Total Discoveries Recorded : {stats['discoveries_count']}")
    print(f"Elapsed Time               : {stats['elapsed_seconds']}s")
    print("=" * 65 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

