"""
Column-schema definitions and documentation for the Exoplanet Atlas pipeline.

This module divides the raw `pscomppars` table from the NASA Exoplanet Archive schema into four logical domains:
    1. Planet Properties
    2. Host-Star Properties
    3. Planetary System Properties
    4. Discovery & Archival Properties

Each column specification includes:
    - name: Canonical column name in the NASA Exoplanet Archive
    - description: Clear plain-language explanation of the parameter
    - unit: Standard astronomical/physical unit
    - domain: 'planet' | 'star' | 'system' | 'discovery'
    - dtype: Recommended Pandas / NumPy nullable dtype

References:
    https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

# Domain Types
Domain = Literal["planet", "star", "system", "discovery"]


@dataclass(frozen=True, slots=True)
class ColumnSpec:
    """Immutable description of a column in the initial schema."""

    name: str
    description: str
    unit: str
    domain: Domain
    dtype: str

    def to_dict(self) -> dict[str, Any]:
        """Convert specification to a plain dictionary."""
        return asdict(self)

# Schema Definition
SCHEMA: list[ColumnSpec] = [
    # 1. PLANET IDENTIFIERS & DISCOVERY FLAGS
    ColumnSpec(
        name="pl_name",
        description=(
            "Planet name as listed in the NASA Exoplanet Archive. "
            "Typically formatted as '<star> <letter>' (e.g. TRAPPIST-1 e, Kepler-186 f)."
        ),
        unit="",
        domain="planet",
        dtype="string",
    ),
    ColumnSpec(
        name="pl_letter",
        description="Planet letter suffix (b, c, d, e, etc.) assigned in order of discovery.",
        unit="",
        domain="planet",
        dtype="string",
    ),
    ColumnSpec(
        name="pl_controv_flag",
        description="Controversy flag: 1 = planet confirmation is debated/questioned in literature; 0 = confirmed.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="tran_flag",
        description="Transit flag: 1 = planet transits its host star as observed from Earth; 0 = no transit detected.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="rv_flag",
        description="Radial velocity flag: 1 = planet detected via Doppler/RV spectroscopy; 0 = not detected via RV.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="ttv_flag",
        description="Transit Timing Variation flag: 1 = timing variations confirmed; 0 = no confirmed TTVs.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="ptv_flag",
        description="Planet Transit Timing Variations flag: 1 = timing variations detected in planetary transits.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="ast_flag",
        description="Astrometry flag: 1 = planet detected via astrometric wobble of the host star.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="micro_flag",
        description="Microlensing flag: 1 = planet detected via gravitational microlensing.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),
    ColumnSpec(
        name="ima_flag",
        description="Direct imaging flag: 1 = planet detected via direct optical/infrared imaging.",
        unit="",
        domain="planet",
        dtype="Int8",
    ),

    # 2. PLANET ORBITAL PROPERTIES
    ColumnSpec(
        name="pl_orbper",
        description="Orbital period: the time required for the planet to complete one full revolution around its star.",
        unit="days",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_orbsmax",
        description="Semi-major axis: the longest semi-diameter of the planet's elliptical orbit.",
        unit="AU",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_orbeccen",
        description="Orbital eccentricity: deviation of the orbit from a perfect circle (0 = circular, 0 < e < 1 = elliptical).",
        unit="",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_orbincl",
        description="Orbital inclination: angle of the orbital plane relative to the plane of the sky (90 deg = edge-on).",
        unit="deg",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_orblper",
        description="Longitude / argument of periastron: angular distance of the periastron from the ascending node.",
        unit="deg",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_orbtper",
        description="Time of periastron passage: Barycentric Julian Date at closest approach.",
        unit="days",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_orbtper_systemref",
        description="Time reference system used for the periastron passage ephemeris (e.g. BJD_TDB).",
        unit="",
        domain="planet",
        dtype="string",
    ),

    # 3. PLANET PHYSICAL & ATMOSPHERIC PROPERTIES
    ColumnSpec(
        name="pl_rade",
        description="Planet equatorial radius measured in Earth radii (1 R_Earth = 6,378.137 km).",
        unit="R_Earth",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_radj",
        description="Planet equatorial radius measured in Jupiter radii (1 R_Jupiter = 71,492 km).",
        unit="R_Jupiter",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_masse",
        description="Planet mass measured in Earth masses (1 M_Earth = 5.9722 x 10^24 kg).",
        unit="M_Earth",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_massj",
        description="Planet mass measured in Jupiter masses (1 M_Jupiter = 1.89813 x 10^27 kg = 317.8 M_Earth).",
        unit="M_Jupiter",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_bmasse",
        description="Best-estimate planet mass in Earth masses (true mass or m*sin(i) lower limit).",
        unit="M_Earth",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_bmassj",
        description="Best-estimate planet mass in Jupiter masses (true mass or m*sin(i) lower limit).",
        unit="M_Jupiter",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_bmassprov",
        description="Provenance of the best-estimate mass: 'Mass' (true mass), 'Msini' (minimum mass), etc.",
        unit="",
        domain="planet",
        dtype="string",
    ),
    ColumnSpec(
        name="pl_msinie",
        description="Minimum mass (m * sin(i)) in Earth masses derived from radial velocity measurements.",
        unit="M_Earth",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_msinij",
        description="Minimum mass (m * sin(i)) in Jupiter masses derived from radial velocity measurements.",
        unit="M_Jupiter",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_dens",
        description="Mean bulk density of the planet computed from mass and radius.",
        unit="g/cm³",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_eqt",
        description="Equilibrium temperature: blackbody surface temperature assuming uniform heat redistribution and zero albedo.",
        unit="K",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_insol",
        description="Insolation flux: stellar irradiance received at the top of the atmosphere relative to Earth solar flux.",
        unit="F_Earth",
        domain="planet",
        dtype="float64",
    ),

    # 4. TRANSIT & OBSERVATIONAL GEOMETRY
    ColumnSpec(
        name="pl_trandur",
        description="Transit duration: total elapsed time from transit ingress to egress.",
        unit="hours",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_trandep",
        description="Transit depth: percentage decrease in stellar flux during mid-transit.",
        unit="%",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_tranmid",
        description="Transit mid-point epoch in Barycentric Julian Date.",
        unit="days",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_tranmid_systemref",
        description="Time standard reference for the transit midpoint (e.g. BJD_TDB).",
        unit="",
        domain="planet",
        dtype="string",
    ),
    ColumnSpec(
        name="pl_ratror",
        description="Ratio of planet radius to stellar radius (Rp / R_star).",
        unit="",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_ratdor",
        description="Ratio of orbital semi-major axis to stellar radius (a / R_star).",
        unit="",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_imppar",
        description="Impact parameter (b): projected distance between planet and stellar centers at transit center in stellar radii.",
        unit="",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_occdep",
        description="Occultation / secondary eclipse depth: fractional brightness decrease when planet passes behind the host star.",
        unit="%",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_rvamp",
        description="Radial velocity semi-amplitude (K) induced on the host star by the orbiting planet.",
        unit="m/s",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_projobliq",
        description="Projected sky obliquity (lambda): angle between stellar spin axis and planetary orbital axis.",
        unit="deg",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_trueobliq",
        description="True 3D stellar obliquity (psi): true angle between stellar spin and orbital angular momentum vectors.",
        unit="deg",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_angsep",
        description="Angular separation between planet and host star on the plane of the sky.",
        unit="arcsec",
        domain="planet",
        dtype="float64",
    ),
    ColumnSpec(
        name="pl_nespec",
        description="Number of emission / secondary eclipse spectra available in the archive.",
        unit="",
        domain="planet",
        dtype="Int16",
    ),
    ColumnSpec(
        name="pl_ntranspec",
        description="Number of transmission spectra available in the archive.",
        unit="",
        domain="planet",
        dtype="Int16",
    ),
    ColumnSpec(
        name="pl_ndispec",
        description="Number of direct-imaging spectra available in the archive.",
        unit="",
        domain="planet",
        dtype="Int16",
    ),
    ColumnSpec(
        name="pl_pubdate",
        description="Publication date of the planet's reference parameters (YYYY-MM).",
        unit="",
        domain="planet",
        dtype="string",
    ),

    # 5. HOST-STAR PROPERTIES
    ColumnSpec(
        name="hostname",
        description="Canonical primary name of the host star.",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="hd_name",
        description="Henry Draper Catalog identifier for the host star.",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="hip_name",
        description="Hipparcos Catalog identifier for the host star.",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="tic_id",
        description="TESS Input Catalog (TIC) source identifier for the host star.",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="gaia_dr2_id",
        description="Gaia Data Release 2 (DR2) source identifier for the host star.",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="gaia_dr3_id",
        description="Gaia Data Release 3 (DR3) source identifier for the host star.",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="st_spectype",
        description="Stellar spectral classification (e.g. G2V, M3.5V, K1IV).",
        unit="",
        domain="star",
        dtype="string",
    ),
    ColumnSpec(
        name="st_teff",
        description="Stellar effective temperature (photospheric blackbody temperature).",
        unit="K",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_rad",
        description="Stellar photospheric radius in solar radii (1 R_Sun = 695,700 km).",
        unit="R_Sun",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_mass",
        description="Stellar mass in solar masses (1 M_Sun = 1.98847 x 10^30 kg).",
        unit="M_Sun",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_met",
        description="Stellar metallicity [Fe/H]: logarithmic ratio of iron-to-hydrogen relative to the Sun.",
        unit="dex",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_logg",
        description="Stellar surface gravity in base-10 logarithmic cgs units (log10(cm/s²)).",
        unit="log10(cm/s²)",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_lum",
        description="Stellar bolometric luminosity in base-10 logarithmic solar luminosities (log10(L_Sun)).",
        unit="log10(L_Sun)",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_age",
        description="Estimated stellar age since zero-age main sequence (ZAMS).",
        unit="Gyr",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_dens",
        description="Mean bulk density of the host star.",
        unit="g/cm³",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_rotp",
        description="Stellar equatorial rotation period.",
        unit="days",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_vsin",
        description="Projected stellar rotational velocity (v * sin(i_star)).",
        unit="km/s",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_radv",
        description="Systemic heliocentric radial velocity of the host star.",
        unit="km/s",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_log_rhk",
        description="Chromospheric activity index log10(R'_HK) derived from Ca II H & K lines.",
        unit="dex",
        domain="star",
        dtype="float64",
    ),
    ColumnSpec(
        name="st_nphot",
        description="Number of photometric time-series records available for this star in the archive.",
        unit="",
        domain="star",
        dtype="Int16",
    ),
    ColumnSpec(
        name="st_nrvc",
        description="Number of radial velocity time-series records available for this star.",
        unit="",
        domain="star",
        dtype="Int16",
    ),
    ColumnSpec(
        name="st_nspec",
        description="Number of stellar spectra available in the archive.",
        unit="",
        domain="star",
        dtype="Int16",
    ),

    # 6. SYSTEM PROPERTIES (COORDINATES, MULTIPLICITY & PHOTOMETRY)
    ColumnSpec(
        name="sy_name",
        description="System designation (usually matches hostname or discovery system name).",
        unit="",
        domain="system",
        dtype="string",
    ),
    ColumnSpec(
        name="ra",
        description="Right Ascension of the system in decimal degrees (ICRS J2000 epoch).",
        unit="deg",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="dec",
        description="Declination of the system in decimal degrees (ICRS J2000 epoch).",
        unit="deg",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_dist",
        description="Distance from the Solar System to the planetary system.",
        unit="pc",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_plx",
        description="Trigonometric parallax of the host star measured by Gaia/Hipparcos.",
        unit="mas",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_pm",
        description="Total proper motion vector magnitude on the celestial sphere.",
        unit="mas/yr",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_pmra",
        description="Proper motion in Right Ascension (pmRA * cos(Dec)).",
        unit="mas/yr",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_pmdec",
        description="Proper motion in Declination.",
        unit="mas/yr",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_snum",
        description="Total number of confirmed stars in the planetary system.",
        unit="",
        domain="system",
        dtype="Int8",
    ),
    ColumnSpec(
        name="sy_pnum",
        description="Total number of confirmed planets in the planetary system.",
        unit="",
        domain="system",
        dtype="Int8",
    ),
    ColumnSpec(
        name="sy_mnum",
        description="Total number of confirmed moons in the planetary system.",
        unit="",
        domain="system",
        dtype="Int8",
    ),
    ColumnSpec(
        name="cb_flag",
        description="Circumbinary flag: 1 = planet orbits two or more stars (P-type orbit); 0 = single star host.",
        unit="",
        domain="system",
        dtype="Int8",
    ),
    # Photometric magnitudes in standard bandpasses
    ColumnSpec(
        name="sy_vmag",
        description="Johnson V-band apparent magnitude (~550 nm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_bmag",
        description="Johnson B-band apparent magnitude (~440 nm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_jmag",
        description="2MASS J-band apparent infrared magnitude (~1.25 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_hmag",
        description="2MASS H-band apparent infrared magnitude (~1.65 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_kmag",
        description="2MASS Ks-band apparent infrared magnitude (~2.16 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_gaiamag",
        description="Gaia G-band broad apparent optical magnitude (~330-1050 nm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_tmag",
        description="TESS passband apparent magnitude (~600-1000 nm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_kepmag",
        description="Kepler passband apparent magnitude (~420-900 nm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_umag",
        description="SDSS u-band apparent ultraviolet magnitude.",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_rmag",
        description="SDSS r-band apparent red magnitude.",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_imag",
        description="SDSS i-band apparent near-infrared magnitude.",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_zmag",
        description="SDSS z-band apparent infrared magnitude.",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_w1mag",
        description="WISE W1 band mid-infrared apparent magnitude (~3.4 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_w2mag",
        description="WISE W2 band mid-infrared apparent magnitude (~4.6 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_w3mag",
        description="WISE W3 band mid-infrared apparent magnitude (~12 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),
    ColumnSpec(
        name="sy_w4mag",
        description="WISE W4 band mid-infrared apparent magnitude (~22 µm).",
        unit="mag",
        domain="system",
        dtype="float64",
    ),

    # 7. DISCOVERY & ARCHIVE METADATA
    ColumnSpec(
        name="discoverymethod",
        description="Primary detection technique (e.g. Transit, Radial Velocity, Microlensing, Direct Imaging).",
        unit="",
        domain="discovery",
        dtype="string",
    ),
    ColumnSpec(
        name="disc_year",
        description="Year in which the planet was published as a confirmed exoplanet.",
        unit="yr",
        domain="discovery",
        dtype="Int16",
    ),
    ColumnSpec(
        name="disc_facility",
        description="Observatory, space telescope mission, or survey facility that discovered the planet.",
        unit="",
        domain="discovery",
        dtype="string",
    ),
    ColumnSpec(
        name="disc_instrument",
        description="Primary astronomical instrument / spectrograph / camera used for discovery.",
        unit="",
        domain="discovery",
        dtype="string",
    ),
    ColumnSpec(
        name="disc_locale",
        description="Discovery platform location: 'Space' or 'Ground'.",
        unit="",
        domain="discovery",
        dtype="string",
    ),
    ColumnSpec(
        name="disc_pubdate",
        description="Date of discovery announcement publication (YYYY-MM).",
        unit="",
        domain="discovery",
        dtype="string",
    ),
    ColumnSpec(
        name="disc_refname",
        description="Bibliographical ADS reference string for the discovery paper.",
        unit="",
        domain="discovery",
        dtype="string",
    ),
]

# Derived Lookups and Helper Functions
def get_schema_names() -> list[str]:
    """Return an ordered list of all column names in the schema."""
    return [spec.name for spec in SCHEMA]


def get_schema_by_domain(domain: Domain) -> list[ColumnSpec]:
    """Filter and return column specifications for a specific domain."""
    return [spec for spec in SCHEMA if spec.domain == domain]


def get_schema_map() -> dict[str, ColumnSpec]:
    """Return a mapping of column name to ColumnSpec."""
    return {spec.name: spec for spec in SCHEMA}


def get_dtype_mapping() -> dict[str, str]:
    """Return a dictionary of column names to recommended pandas dtypes."""
    return {spec.name: spec.dtype for spec in SCHEMA}


def build_curated_select_clause() -> str:
    """
    Build the SQL SELECT clause string containing all curated schema columns.

    Returns:
        e.g. 'pl_name, pl_letter, pl_controv_flag, ...'
    """
    return ", ".join(get_schema_names())


def get_schema_dictionary() -> dict[str, dict[str, Any]]:
    """
    Return a machine-readable data dictionary of the initial schema.
    """
    return {spec.name: spec.to_dict() for spec in SCHEMA}
