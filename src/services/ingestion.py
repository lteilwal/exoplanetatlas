"""
Database Ingestion Service.

Reads cleaned dataset from Stage 1 (`exoplanets_processed.csv`),
normalizes into relational entities (System, Star, Planet, Discovery),
and populates/updates PostgreSQL/SQLite with deduplication and upserts.
"""
from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.session import SessionLocal, init_db
from src.models import Discovery, Planet, Star, System

logger = logging.getLogger(__name__)


def _sanitize_val(val: Any) -> Any:
    """Convert pandas NaN, NaT, and float('nan') to Python None."""
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if pd.isna(val):
        return None
    return val


def _process_dataframe(df: pd.DataFrame, db: Session, batch_size: int = 500) -> dict[str, int]:
    """
    Parse DataFrame records and insert into relational models.
    """
    systems_cache: Dict[str, System] = {}
    stars_cache: Dict[str, Star] = {}

    # Pre-cache existing systems
    for sys in db.scalars(select(System)).all():
        systems_cache[sys.name] = sys

    # Pre-cache existing stars
    for star in db.scalars(select(Star)).all():
        stars_cache[star.name] = star

    total_rows = len(df)
    logger.info(f"Starting ingestion of {total_rows} records into database...")

    for idx, row in df.iterrows():
        
        # 1. System entity
        sys_name = _sanitize_val(row.get("sy_name")) or _sanitize_val(row.get("hostname")) or _sanitize_val(row.get("pl_name"))
        if not sys_name:
            continue

        if sys_name not in systems_cache:
            system = System(
                name=sys_name,
                ra=_sanitize_val(row.get("ra")),
                dec=_sanitize_val(row.get("dec")),
                distance_pc=_sanitize_val(row.get("sy_dist")),
                parallax_mas=_sanitize_val(row.get("sy_plx")),
                proper_motion_mas_yr=_sanitize_val(row.get("sy_pm")),
                proper_motion_ra=_sanitize_val(row.get("sy_pmra")),
                proper_motion_dec=_sanitize_val(row.get("sy_pmdec")),
                star_count=int(_sanitize_val(row.get("sy_snum")) or 1),
                planet_count=int(_sanitize_val(row.get("sy_pnum")) or 1),
                moon_count=int(_sanitize_val(row.get("sy_mnum")) or 0),
                is_circumbinary=bool(_sanitize_val(row.get("cb_flag")) == 1),
                v_mag=_sanitize_val(row.get("sy_vmag")),
                b_mag=_sanitize_val(row.get("sy_bmag")),
                j_mag=_sanitize_val(row.get("sy_jmag")),
                h_mag=_sanitize_val(row.get("sy_hmag")),
                k_mag=_sanitize_val(row.get("sy_kmag")),
                gaia_mag=_sanitize_val(row.get("sy_gaiamag")),
                tess_mag=_sanitize_val(row.get("sy_tmag")),
                kepler_mag=_sanitize_val(row.get("sy_kmag")),
            )
            db.add(system)
            db.flush()
            systems_cache[sys_name] = system
        else:
            system = systems_cache[sys_name]

        # 2. Host Star entity
        star_name = _sanitize_val(row.get("hostname")) or sys_name
        if star_name not in stars_cache:
            star = Star(
                system_id=system.id,
                name=star_name,
                hd_id=_sanitize_val(row.get("hd_name")),
                hip_id=_sanitize_val(row.get("hip_name")),
                tic_id=_sanitize_val(row.get("tic_id")),
                gaia_dr2_id=_sanitize_val(row.get("gaia_dr2_id")),
                gaia_dr3_id=_sanitize_val(row.get("gaia_dr3_id")),
                spectral_type=_sanitize_val(row.get("st_spectype")),
                effective_temp_k=_sanitize_val(row.get("st_teff")),
                radius_solar=_sanitize_val(row.get("st_rad")),
                mass_solar=_sanitize_val(row.get("st_mass")),
                metallicity_dex=_sanitize_val(row.get("st_met")),
                surface_gravity_logg=_sanitize_val(row.get("st_logg")),
                luminosity_log_solar=_sanitize_val(row.get("st_lum")),
                age_gyr=_sanitize_val(row.get("st_age")),
                density_g_cm3=_sanitize_val(row.get("st_dens")),
                rotation_period_days=_sanitize_val(row.get("st_rotp")),
                v_sin_i_km_s=_sanitize_val(row.get("st_vsin")),
                radial_velocity_km_s=_sanitize_val(row.get("st_radv")),
            )
            db.add(star)
            db.flush()
            stars_cache[star_name] = star
        else:
            star = stars_cache[star_name]

        # 3. Planet entity
        pl_name = _sanitize_val(row.get("pl_name"))
        if not pl_name:
            continue

        existing_planet = db.scalar(select(Planet).where(Planet.name == pl_name))
        if existing_planet:
            planet = existing_planet
            # Update fields
            planet.system_id = system.id
            planet.star_id = star.id
        else:
            planet = Planet(
                system_id=system.id,
                star_id=star.id,
                name=pl_name,
            )
            db.add(planet)

        planet.planet_letter = _sanitize_val(row.get("pl_letter"))
        planet.is_controversial = bool(_sanitize_val(row.get("pl_controv_flag")) == 1)
        planet.orbital_period_days = _sanitize_val(row.get("pl_orbper"))
        planet.semi_major_axis_au = _sanitize_val(row.get("pl_orbsmax"))
        planet.eccentricity = _sanitize_val(row.get("pl_orbeccen"))
        planet.inclination_deg = _sanitize_val(row.get("pl_orbincl"))
        planet.longitude_periastron_deg = _sanitize_val(row.get("pl_orblper"))
        planet.periastron_passage_days = _sanitize_val(row.get("pl_orbtper"))
        planet.radius_earth = _sanitize_val(row.get("pl_rade"))
        planet.radius_jupiter = _sanitize_val(row.get("pl_radj"))
        planet.mass_earth = _sanitize_val(row.get("pl_masse"))
        planet.mass_jupiter = _sanitize_val(row.get("pl_massj"))
        planet.best_mass_earth = _sanitize_val(row.get("pl_bmasse"))
        planet.best_mass_jupiter = _sanitize_val(row.get("pl_bmassj"))
        planet.mass_provenance = _sanitize_val(row.get("pl_bmassprov"))
        planet.msini_earth = _sanitize_val(row.get("pl_msinie"))
        planet.msini_jupiter = _sanitize_val(row.get("pl_msinij"))
        planet.density_g_cm3 = _sanitize_val(row.get("pl_dens")) or _sanitize_val(row.get("calc_density"))
        planet.equilibrium_temp_k = _sanitize_val(row.get("pl_eqt"))
        planet.insolation_earth = _sanitize_val(row.get("pl_insol"))
        planet.transit_duration_hours = _sanitize_val(row.get("pl_trandur"))
        planet.transit_depth_percent = _sanitize_val(row.get("pl_trandep"))
        planet.transit_midpoint_days = _sanitize_val(row.get("pl_tranmid"))
        planet.impact_parameter = _sanitize_val(row.get("pl_imppar"))
        planet.ratio_planet_to_star_radius = _sanitize_val(row.get("pl_ratror"))
        planet.radial_velocity_amplitude_m_s = _sanitize_val(row.get("pl_rvamp"))
        planet.planet_class = _sanitize_val(row.get("planet_class"))
        planet.habitability_zone_est = _sanitize_val(row.get("habitability_zone_est"))
        planet.tran_flag = bool(_sanitize_val(row.get("tran_flag")) == 1)
        planet.rv_flag = bool(_sanitize_val(row.get("rv_flag")) == 1)
        planet.ttv_flag = bool(_sanitize_val(row.get("ttv_flag")) == 1)
        planet.ptv_flag = bool(_sanitize_val(row.get("ptv_flag")) == 1)
        planet.ast_flag = bool(_sanitize_val(row.get("ast_flag")) == 1)
        planet.micro_flag = bool(_sanitize_val(row.get("micro_flag")) == 1)
        planet.ima_flag = bool(_sanitize_val(row.get("ima_flag")) == 1)

        db.flush()

        # 4. Discovery entity (1-to-1 with Planet)
        disc_method = _sanitize_val(row.get("discoverymethod")) or "Unknown"
        existing_disc = db.scalar(select(Discovery).where(Discovery.planet_id == planet.id))
        if existing_disc:
            disc = existing_disc
        else:
            disc = Discovery(planet_id=planet.id, discovery_method=disc_method)
            db.add(disc)

        disc.discovery_method = disc_method
        disc.discovery_year = int(_sanitize_val(row.get("disc_year"))) if _sanitize_val(row.get("disc_year")) else None
        disc.discovery_facility = _sanitize_val(row.get("disc_facility"))
        disc.discovery_instrument = _sanitize_val(row.get("disc_instrument"))
        disc.discovery_locale = _sanitize_val(row.get("disc_locale"))
        disc.publication_date = str(_sanitize_val(row.get("disc_pubdate"))) if _sanitize_val(row.get("disc_pubdate")) else None
        disc.reference_name = _sanitize_val(row.get("disc_refname"))

        if idx > 0 and idx % batch_size == 0:
            db.commit()
            logger.info(f"Ingested {idx}/{total_rows} rows...")

    db.commit()
    logger.info("Ingestion transaction committed successfully.")

    return {
        "rows_processed": total_rows,
        "systems_count": db.scalar(select(System).count()) if hasattr(select(System), "count") else len(systems_cache),
        "stars_count": len(stars_cache),
        "planets_count": db.query(Planet).count(),
        "discoveries_count": db.query(Discovery).count(),
    }


def ingest_from_csv(
    csv_path: Optional[Path | str] = None,
    db: Optional[Session] = None,
    batch_size: int = 500,
) -> dict[str, Any]:
    """
    Ingest exoplanet CSV dataset into the relational database.
    """
    start_time = time.time()
    source_file = Path(csv_path) if csv_path else settings.PROCESSED_CSV_PATH

    if not source_file.exists():
        raise FileNotFoundError(
            f"Ingestion source file not found at: {source_file}. "
            f"Run 'python run_pipeline.py' first to acquire and process the data."
        )

    logger.info(f"Loading data for ingestion from: {source_file}")
    df = pd.read_csv(source_file, low_memory=False)
    logger.info(f"Read {len(df)} rows to ingest into relational database.")

    should_close_session = False
    if db is None:
        db = SessionLocal()
        should_close_session = True

    # Initialize tables if necessary
    init_db(target_engine=db.get_bind())

    try:
        stats = _process_dataframe(df=df, db=db, batch_size=batch_size)
        elapsed = round(time.time() - start_time, 2)
        stats["elapsed_seconds"] = elapsed
        logger.info(
            f"Ingestion finished in {elapsed}s: {stats['systems_count']} systems, "
            f"{stats['stars_count']} stars, {stats['planets_count']} planets, "
            f"{stats['discoveries_count']} discoveries."
        )
        return stats
    finally:
        if should_close_session:
            db.close()

