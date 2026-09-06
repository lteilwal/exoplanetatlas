"""
Data processing, cleaning, and validation pipeline for the Exoplanet Atlas Stage 1.

Performs:
    1. Whitespace and null value sanitization
    2. Physical validation and anomaly filtration
    3. Derived astronomical parameter calculations (classification, habitability, density)
    4. Explicit schema alignment and dtype enforcement
    5. Comprehensive metadata & data hygiene reporting
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from . import config
from .schema import (
    SCHEMA,
    Domain,
    get_dtype_mapping,
    get_schema_dictionary,
    get_schema_names,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Physical Validation Thresholds
# ---------------------------------------------------------------------------
MAX_REASONABLE_PLANET_RADIUS_RJ: float = 30.0  # Gas giants rarely exceed ~2.5-3 R_J; brown dwarfs up to ~30 R_E / 3 R_J
MAX_REASONABLE_PLANET_MASS_MJ: float = 80.0    # Deuterium fusion boundary is ~13 M_J; hydrogen burning is ~80 M_J

def sanitize_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Normalise column names, clean strings, and convert empty/sentinel values to NaN.

    Parameters
    ----------
    df : pd.DataFrame
        Input raw DataFrame.

    Returns
    -------
    tuple[pd.DataFrame, list[str]]
        Sanitized DataFrame and list of performed actions.
    """
    actions: list[str] = []
    cleaned_df = df.copy()

    # 1. Clean column names
    cleaned_df.columns = cleaned_df.columns.str.strip()
    actions.append("Normalized column names by stripping leading/trailing whitespace")

    # 2. Convert common string representations of missing values to NaN
    str_cols = cleaned_df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        cleaned_df[col] = cleaned_df[col].replace(
            {"nan": np.nan, "NaN": np.nan, "null": np.nan, "NULL": np.nan, "None": np.nan, "": np.nan}
        )

    actions.append(f"Sanitized string null sentinels across {len(str_cols)} string columns")
    return cleaned_df, actions

def filter_and_validate(
    df: pd.DataFrame,
    strict_filters: bool = False,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Validate physical boundaries and apply quality filters.

    In standard mode (default), non-physical negative values (e.g. negative period or radius)
    are replaced with NaN rather than dropping valid confirmed planets, preserving coverage.
    In strict mode, rows lacking fundamental parameters are excluded.

    Parameters
    ----------
    df : pd.DataFrame
        Sanitized DataFrame.
    strict_filters : bool, default False
        If True, drops rows with missing orbital period or mass/radius.

    Returns
    -------
    tuple[pd.DataFrame, list[str]]
        Validated DataFrame and list of actions.
    """
    actions: list[str] = []
    val_df = df.copy()
    initial_count = len(val_df)

    # Must have a valid planet name
    if "pl_name" in val_df.columns:
        val_df = val_df[val_df["pl_name"].notna() & (val_df["pl_name"].str.len() > 0)]
        dropped_names = initial_count - len(val_df)
        if dropped_names > 0:
            actions.append(f"Dropped {dropped_names} records with missing planet name")

    # Numerical columns that must be strictly positive (> 0)
    positive_cols = [
        "pl_orbper", "pl_orbsmax", "pl_rade", "pl_radj",
        "pl_masse", "pl_massj", "pl_bmasse", "pl_bmassj",
        "pl_dens", "st_rad", "st_mass", "st_teff", "sy_dist", "pl_trandur"
    ]

    for col in positive_cols:
        if col in val_df.columns:
            val_df[col] = pd.to_numeric(val_df[col], errors="coerce")
            invalid_mask = val_df[col] <= 0
            invalid_count = int(invalid_mask.sum())
            if invalid_count > 0:
                val_df.loc[invalid_mask, col] = np.nan
                actions.append(f"Replaced {invalid_count} non-positive values in '{col}' with NaN")

    # Bounded physical variables: Eccentricity must be in [0, 1) for bound orbits
    if "pl_orbeccen" in val_df.columns:
        val_df["pl_orbeccen"] = pd.to_numeric(val_df["pl_orbeccen"], errors="coerce")
        ecc_invalid = (val_df["pl_orbeccen"] < 0) | (val_df["pl_orbeccen"] >= 1.0)
        ecc_count = int(ecc_invalid.sum())
        if ecc_count > 0:
            val_df.loc[ecc_invalid, "pl_orbeccen"] = np.nan
            actions.append(f"Replaced {ecc_count} invalid eccentricities outside [0, 1) with NaN")

    # Inclination: [0, 180] degrees
    if "pl_orbincl" in val_df.columns:
        val_df["pl_orbincl"] = pd.to_numeric(val_df["pl_orbincl"], errors="coerce")
        incl_invalid = (val_df["pl_orbincl"] < 0) | (val_df["pl_orbincl"] > 180.0)
        incl_count = int(incl_invalid.sum())
        if incl_count > 0:
            val_df.loc[incl_invalid, "pl_orbincl"] = np.nan
            actions.append(f"Replaced {incl_count} invalid inclinations outside [0, 180] with NaN")

    # Transit depth: [0, 100]%
    if "pl_trandep" in val_df.columns:
        val_df["pl_trandep"] = pd.to_numeric(val_df["pl_trandep"], errors="coerce")
        dep_invalid = (val_df["pl_trandep"] < 0) | (val_df["pl_trandep"] > 100.0)
        dep_count = int(dep_invalid.sum())
        if dep_count > 0:
            val_df.loc[dep_invalid, "pl_trandep"] = np.nan
            actions.append(f"Replaced {dep_count} invalid transit depths with NaN")

    # Quality filter: remove extreme outliers exceeding theoretical upper limits
    if "pl_radj" in val_df.columns:
        rad_outliers = val_df["pl_radj"] > MAX_REASONABLE_PLANET_RADIUS_RJ
        rad_outlier_count = int(rad_outliers.sum())
        if rad_outlier_count > 0:
            val_df.loc[rad_outliers, "pl_radj"] = np.nan
            if "pl_rade" in val_df.columns:
                val_df.loc[rad_outliers, "pl_rade"] = np.nan
            actions.append(f"Nullified {rad_outlier_count} extreme radius outliers (> {MAX_REASONABLE_PLANET_RADIUS_RJ} R_J)")

    # Strict mode filter if requested
    if strict_filters:
        before_strict = len(val_df)
        if "pl_orbper" in val_df.columns:
            val_df = val_df[val_df["pl_orbper"].notna()]
        if "st_mass" in val_df.columns:
            val_df = val_df[val_df["st_mass"].notna()]
        dropped_strict = before_strict - len(val_df)
        if dropped_strict > 0:
            actions.append(f"Strict filter: dropped {dropped_strict} rows lacking period or stellar mass")

    return val_df, actions


def add_derived_astronomical_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Calculate derived astronomical properties and classifications.

    Adds:
        - planet_class: Planet physical size classification
          (Terrestrial, Super-Earth, Sub-Neptune, Neptune-like, Gas Giant)
        - habitability_zone_est: Stellar insolation regime
          (Conservative Habitable Zone, Optimistic Habitable Zone, Hot Zone, Cold Zone)
        - calc_density: Calculated bulk density (g/cm³) when pl_dens is missing

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    tuple[pd.DataFrame, list[str]]
        Enriched DataFrame and action notes.
    """
    actions: list[str] = []
    res_df = df.copy()

    # 1. Calculated Bulk Density (g/cm³)
    # Earth bulk density = 5.514 g/cm³
    # rho = 5.514 * (Mass_Earth) / (Radius_Earth ^ 3)
    if "pl_rade" in res_df.columns and ("pl_bmasse" in res_df.columns or "pl_masse" in res_df.columns):
        mass_col = "pl_bmasse" if "pl_bmasse" in res_df.columns else "pl_masse"
        mass_val = pd.to_numeric(res_df[mass_col], errors="coerce")
        rad_val = pd.to_numeric(res_df["pl_rade"], errors="coerce")

        computed_rho = 5.514 * mass_val / (rad_val ** 3)
        # Cap to plausible planetary densities (0.01 to 30 g/cm³)
        computed_rho = computed_rho.where((computed_rho >= 0.01) & (computed_rho <= 30.0), np.nan)

        if "pl_dens" in res_df.columns:
            res_df["calc_density"] = res_df["pl_dens"].fillna(computed_rho.round(3))
        else:
            res_df["calc_density"] = computed_rho.round(3)

        filled_count = int(res_df["calc_density"].notna().sum())
        actions.append(f"Derived 'calc_density' (available for {filled_count} planets)")

    # 2. Planet Size & Mass Classification
    def classify_planet(row: pd.Series) -> str:
        rade = row.get("pl_rade")
        masse = row.get("pl_bmasse") if pd.notna(row.get("pl_bmasse")) else row.get("pl_masse")

        if pd.notna(rade):
            if rade < 1.25:
                return "Terrestrial"
            elif rade < 2.0:
                return "Super-Earth"
            elif rade < 4.0:
                return "Sub-Neptune"
            elif rade < 6.0:
                return "Neptune-like"
            else:
                return "Gas Giant"
        elif pd.notna(masse):
            if masse < 2.0:
                return "Terrestrial"
            elif masse < 10.0:
                return "Super-Earth"
            elif masse < 50.0:
                return "Neptune-like"
            else:
                return "Gas Giant"
        return "Unknown"

    res_df["planet_class"] = res_df.apply(classify_planet, axis=1).astype("string")
    actions.append("Classified planets into morphological types ('planet_class')")

    # 3. Insolation & Habitability Zone Estimation
    # Based on Kopparapu et al. insolation flux relative to Earth (S_eff):
    # Conservative HZ: 0.35 <= S_eff <= 1.11 (Runaway greenhouse to Maximum greenhouse)
    # Optimistic HZ: 0.32 <= S_eff < 0.35 (Early Mars) or 1.11 < S_eff <= 1.78 (Recent Venus)
    def classify_habitability(row: pd.Series) -> str:
        insol = row.get("pl_insol")
        if pd.isna(insol):
            eqt = row.get("pl_eqt")
            if pd.notna(eqt):
                if 200 <= eqt <= 320:
                    return "Potential Habitable (Equilibrium Temp)"
                elif eqt > 320:
                    return "Hot Zone"
                else:
                    return "Cold Zone"
            return "Unknown"

        insol = float(insol)
        if 0.35 <= insol <= 1.11:
            return "Conservative Habitable Zone"
        elif (0.32 <= insol < 0.35) or (1.11 < insol <= 1.78):
            return "Optimistic Habitable Zone"
        elif insol > 1.78:
            return "Hot Zone"
        else:
            return "Cold Zone"

    res_df["habitability_zone_est"] = res_df.apply(classify_habitability, axis=1).astype("string")
    actions.append("Evaluated stellar insolation regime ('habitability_zone_est')")

    return res_df, actions


def enforce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce explicit pandas nullable dtypes across all schema columns.
    """
    typed_df = df.copy()
    dtype_map = get_dtype_mapping()

    for col, target_dtype in dtype_map.items():
        if col not in typed_df.columns:
            continue

        try:
            if target_dtype in ("Int8", "Int16", "Int32", "Int64"):
                typed_df[col] = pd.to_numeric(typed_df[col], errors="coerce").astype(target_dtype)
            elif target_dtype == "float64":
                typed_df[col] = pd.to_numeric(typed_df[col], errors="coerce").astype("float64")
            elif target_dtype == "string":
                typed_df[col] = typed_df[col].astype("string")
        except Exception as exc:
            logger.debug(f"Could not convert column '{col}' to {target_dtype}: {exc}")

    return typed_df


def select_schema_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Align the DataFrame columns strictly with the initial schema plus derived columns.

    Ordering:
        1. All schema columns in canonical schema order
        2. Derived feature columns ('planet_class', 'habitability_zone_est', 'calc_density')
    """
    schema_names = get_schema_names()
    derived_cols = ["planet_class", "habitability_zone_est", "calc_density"]

    aligned_df = pd.DataFrame(index=df.index)

    # Add schema columns (filling with NaN if missing from source query)
    for col in schema_names:
        if col in df.columns:
            aligned_df[col] = df[col]
        else:
            aligned_df[col] = np.nan

    # Add derived columns if present
    for col in derived_cols:
        if col in df.columns:
            aligned_df[col] = df[col]

    return aligned_df


def clean_dataframe(
    df: pd.DataFrame,
    strict_filters: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Execute full cleaning, validation, enrichment, and schema alignment.

    Parameters
    ----------
    df : pd.DataFrame
        Raw ingested DataFrame.
    strict_filters : bool, default False
        Whether to discard rows missing period/mass.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, Any]]
        Cleaned, schema-aligned DataFrame and complete metadata report.
    """
    all_actions: list[str] = []
    start_time = time.time()
    input_rows = len(df)

    # 1. Sanitize values
    sanitized_df, acts = sanitize_dataframe(df)
    all_actions.extend(acts)

    # 2. Filter & validate
    validated_df, acts = filter_and_validate(sanitized_df, strict_filters=strict_filters)
    all_actions.extend(acts)

    # 3. Add derived astronomical parameters
    enriched_df, acts = add_derived_astronomical_features(validated_df)
    all_actions.extend(acts)

    # 4. Align with canonical schema and derived columns
    schema_df = select_schema_columns(enriched_df)

    # 5. Enforce explicit dtypes
    typed_df = enforce_dtypes(schema_df)

    # 6. Deterministic sorting: hostname ASC, pl_letter ASC, pl_name ASC
    sort_cols = [c for c in ["hostname", "pl_letter", "pl_name"] if c in typed_df.columns]
    if sort_cols:
        typed_df = typed_df.sort_values(by=sort_cols, ascending=True).reset_index(drop=True)
        all_actions.append(f"Sorted dataset deterministically by {', '.join(sort_cols)}")

    elapsed = time.time() - start_time
    output_rows = len(typed_df)

    # 7. Generate comprehensive metadata
    metadata = compute_dataset_metadata(
        df=typed_df,
        input_rows=input_rows,
        output_rows=output_rows,
        actions=all_actions,
        elapsed_seconds=elapsed,
    )

    logger.info(
        f"Data cleaning complete: {input_rows} input -> {output_rows} output rows "
        f"({metadata['completeness_overall_pct']:.1f}% overall cell completeness)"
    )

    return typed_df, metadata


def compute_dataset_metadata(
    df: pd.DataFrame,
    input_rows: int,
    output_rows: int,
    actions: list[str],
    elapsed_seconds: float,
) -> dict[str, Any]:
    """
    Generate rich metadata describing data hygiene, distributions, and domain completeness.
    """
    total_cells = df.shape[0] * df.shape[1]
    nan_cells = int(df.isna().sum().sum())
    valid_cells = total_cells - nan_cells
    completeness_overall = round(100.0 * valid_cells / total_cells, 2) if total_cells > 0 else 0.0

    # Domain completeness breakdown
    domain_stats: dict[str, dict[str, Any]] = {}
    for spec in SCHEMA:
        col = spec.name
        dom = spec.domain
        if dom not in domain_stats:
            domain_stats[dom] = {"total_columns": 0, "filled_cells": 0, "total_cells": 0}

        if col in df.columns:
            domain_stats[dom]["total_columns"] += 1
            filled = int(df[col].notna().sum())
            total = len(df)
            domain_stats[dom]["filled_cells"] += filled
            domain_stats[dom]["total_cells"] += total

    for dom, stats in domain_stats.items():
        tot = stats["total_cells"]
        stats["completeness_pct"] = round(100.0 * stats["filled_cells"] / tot, 2) if tot > 0 else 0.0

    # Summary distributions
    discovery_methods = (
        df["discoverymethod"].value_counts().to_dict() if "discoverymethod" in df.columns else {}
    )
    planet_classes = (
        df["planet_class"].value_counts().to_dict() if "planet_class" in df.columns else {}
    )
    habitability_breakdown = (
        df["habitability_zone_est"].value_counts().to_dict() if "habitability_zone_est" in df.columns else {}
    )

    unique_hosts = int(df["hostname"].nunique()) if "hostname" in df.columns else 0
    multi_planet_systems = 0
    if "hostname" in df.columns:
        counts = df["hostname"].value_counts()
        multi_planet_systems = int((counts > 1).sum())

    discovery_year_min = int(df["disc_year"].min()) if "disc_year" in df.columns and df["disc_year"].notna().any() else None
    discovery_year_max = int(df["disc_year"].max()) if "disc_year" in df.columns and df["disc_year"].notna().any() else None

    # Column-level coverage
    column_coverage: dict[str, dict[str, Any]] = {}
    for col in df.columns:
        non_null = int(df[col].notna().sum())
        column_coverage[col] = {
            "non_null_count": non_null,
            "null_count": int(df[col].isna().sum()),
            "coverage_pct": round(100.0 * non_null / len(df), 2) if len(df) > 0 else 0.0,
            "dtype": str(df[col].dtype),
        }

    return {
        "pipeline_stage": "Stage 1: Data Acquisition & Processing",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_archive": "NASA Exoplanet Archive (TAP API)",
        "source_table": config.DEFAULT_TABLE,
        "input_rows": input_rows,
        "output_rows": output_rows,
        "rows_removed": input_rows - output_rows,
        "unique_host_stars": unique_hosts,
        "multi_planet_systems": multi_planet_systems,
        "discovery_year_range": [discovery_year_min, discovery_year_max],
        "completeness_overall_pct": completeness_overall,
        "domain_completeness": domain_stats,
        "planet_classification_distribution": planet_classes,
        "habitability_zone_distribution": habitability_breakdown,
        "discovery_method_distribution": discovery_methods,
        "actions_performed": actions,
        "processing_time_seconds": round(elapsed_seconds, 3),
        "columns_count": df.shape[1],
        "column_coverage": column_coverage,
    }


def save_processed(
    df: pd.DataFrame,
    metadata: dict[str, Any],
    csv_path: Optional[str | Path] = None,
    json_path: Optional[str | Path] = None,
    dict_path: Optional[str | Path] = None,
) -> tuple[str, str, str]:
    """
    Save the cleaned dataset, metadata report, and data dictionary to disk.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.
    metadata : dict[str, Any]
        Pipeline metadata dictionary.
    csv_path : str or Path, optional
        Target CSV path.
    json_path : str or Path, optional
        Target metadata JSON path.
    dict_path : str or Path, optional
        Target data dictionary JSON path.

    Returns
    -------
    tuple[str, str, str]
        Filepaths to CSV, metadata JSON, and data dictionary JSON.
    """
    target_csv = Path(csv_path) if csv_path else config.PROCESSED_PLANETS_FILE
    target_json = Path(json_path) if json_path else config.PROCESSED_METADATA_FILE
    target_dict = Path(dict_path) if dict_path else config.DATA_DICTIONARY_FILE

    target_csv.parent.mkdir(parents=True, exist_ok=True)

    # Save CSV
    df.to_csv(target_csv, index=False)
    logger.info(f"Saved processed dataset: {target_csv} ({len(df)} rows, {df.shape[1]} columns)")

    # Save Metadata JSON
    with open(target_json, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)
    logger.info(f"Saved dataset metadata report: {target_json}")

    # Save Data Dictionary JSON
    data_dict = get_schema_dictionary()
    with open(target_dict, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, default=str)
    logger.info(f"Saved schema data dictionary: {target_dict}")

    return str(target_csv), str(target_json), str(target_dict)