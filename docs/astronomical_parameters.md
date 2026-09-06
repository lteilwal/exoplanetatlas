# Astronomical Parameter Reference Guide

This document defines and explains the astronomical parameters curated in **Stage 1** of the **Exoplanet Atlas** project. The dataset is ingested from the NASA Exoplanet Archive's `pscomppars` (Planetary Systems Composite Parameters) table.

Parameters are organized into four primary domains, followed by derived classifications.

---

## 1. Planet Properties (`domain: planet`)

### Identifiers & Flags
- **`pl_name`**: The canonical name of the exoplanet (e.g., *TRAPPIST-1 e*, *Kepler-452 b*, *HD 209458 b*). Typically formatted as the host star name followed by a lowercase letter (`b`, `c`, `d`, etc.).
- **`pl_letter`**: The letter suffix indicating the order of discovery or orbital hierarchy within the multi-planet system (starting with `b`).
- **`pl_controv_flag`**: Controversy flag ($1 = \text{controversial/debated}$; $0 = \text{confirmed}$). Indicates whether the physical existence of the planet is debated in peer-reviewed astronomical literature.
- **`tran_flag`**: Observed in primary transit flag ($1 = \text{confirmed transit}$; $0 = \text{no transit}$).
- **`rv_flag`**: Radial velocity flag ($1 = \text{detected via RV/Doppler}$; $0 = \text{not detected via RV}$).
- **`ttv_flag`**: Transit Timing Variation flag ($1 = \text{confirmed TTVs}$; $0 = \text{none}$).
- **`ptv_flag`**: Planet Transit Timing Variations flag.
- **`ast_flag`**: Astrometric detection flag ($1 = \text{detected via stellar astrometric wobble}$).
- **`micro_flag`**: Gravitational microlensing detection flag ($1 = \text{detected via microlensing}$).
- **`ima_flag`**: Direct imaging flag ($1 = \text{detected via direct imaging}$).

### Orbital Dynamics
- **`pl_orbper`** $[ \text{days} ]$: Orbital period — the time taken by the planet to complete one full orbit around its host star.
- **`pl_orbsmax`** $[ \text{AU} ]$: Semi-major axis — the mean distance between the planet and the barycenter/host star ($1\text{ AU} \approx 1.496 \times 10^8\text{ km}$).
- **`pl_orbeccen`**: Orbital eccentricity ($0 \le e < 1$ for bound orbits). $e=0$ represents a circular orbit; higher values represent increasingly elongated ellipses.
- **`pl_orbincl`** $[ \text{degrees} ]$: Orbital inclination — the tilt of the planet's orbital plane relative to the plane perpendicular to the line of sight from Earth ($i = 90^\circ$ corresponds to an edge-on transit geometry).
- **`pl_orblper`** $[ \text{degrees} ]$: Argument / longitude of periastron ($\omega$) — the angular position of periastron (closest orbital approach) relative to the ascending node.
- **`pl_orbtper`** $[ \text{days / BJD} ]$: Time of periastron passage expressed in Barycentric Julian Date.
- **`pl_orbtper_systemref`**: Time standard used for the periastron reference (e.g., `BJD_TDB`).

### Physical & Atmospheric Properties
- **`pl_rade`** $[ R_\oplus ]$: Planet equatorial radius measured in Earth radii ($1\, R_\oplus = 6,378.137\text{ km}$).
- **`pl_radj`** $[ R_J ]$: Planet equatorial radius measured in Jupiter radii ($1\, R_J = 71,492\text{ km} \approx 11.209\, R_\oplus$).
- **`pl_masse`** $[ M_\oplus ]$: Planet mass measured in Earth masses ($1\, M_\oplus = 5.9722 \times 10^{24}\text{ kg}$).
- **`pl_massj`** $[ M_J ]$: Planet mass measured in Jupiter masses ($1\, M_J = 1.89813 \times 10^{27}\text{ kg} \approx 317.83\, M_\oplus$).
- **`pl_bmasse`** / **`pl_bmassj`**: Best-estimate planet mass (Earth/Jupiter units). Represents either true dynamical mass or the radial-velocity minimum mass ($M \sin i$).
- **`pl_bmassprov`**: Provenance of the best mass measurement (e.g., `'Mass'` for true mass, `'Msini'` for minimum Doppler mass).
- **`pl_msinie`** / **`pl_msinij`**: Minimum planetary mass ($M \sin i$) derived from Doppler spectroscopy.
- **`pl_dens`** $[ \text{g/cm}^3 ]$: Bulk mean density of the planet ($\rho = M / V$). For comparison, Earth is $5.514\text{ g/cm}^3$, water is $1.0\text{ g/cm}^3$, and Saturn is $0.687\text{ g/cm}^3$.
- **`pl_eqt`** $[ \text{K} ]$: Planetary equilibrium temperature — the theoretical blackbody temperature of the planet assuming uniform thermal redistribution and zero Bond albedo:
  $$T_{\text{eq}} = T_{\text{eff}} \sqrt{\frac{R_\star}{2a}}$$
- **`pl_insol`** $[ F_\oplus ]$: Stellar insolation flux — the total stellar irradiance received at the top of the planet's atmosphere normalized to the solar flux received by Earth ($1\, F_\oplus = 1361\text{ W/m}^2$).

### Transit & Observational Geometry
- **`pl_trandur`** $[ \text{hours} ]$: Total transit duration from first contact (ingress) to fourth contact (egress).
- **`pl_trandep`** $[ \% ]$: Transit depth — the percentage drop in the host star's brightness during mid-transit ($\Delta F / F \approx (R_p / R_\star)^2$).
- **`pl_tranmid`** $[ \text{days / BJD} ]$: Mid-transit epoch in Barycentric Julian Date.
- **`pl_ratror`**: Planet-to-star radius ratio ($R_p / R_\star$).
- **`pl_ratdor`**: Scaled semi-major axis ($a / R_\star$).
- **`pl_imppar`**: Impact parameter ($b = \frac{a \cos i}{R_\star} \frac{1 - e^2}{1 + e \sin \omega}$) — the projected distance between the planetary and stellar centers at transit midpoint in units of stellar radii ($b \le 1$ for a transit).
- **`pl_occdep`** $[ \% ]$: Occultation / secondary eclipse depth observed when the planet passes behind the host star.
- **`pl_rvamp`** $[ \text{m/s} ]$: Radial velocity semi-amplitude ($K$) of the Doppler reflex motion induced on the star.
- **`pl_projobliq`** $[ \text{deg} ]$: Sky-projected stellar obliquity ($\lambda$) measured via the Rossiter-McLaughlin effect.
- **`pl_trueobliq`** $[ \text{deg} ]$: True 3D angle ($\psi$) between the stellar rotational axis and orbital angular momentum vector.
- **`pl_angsep`** $[ \text{arcsec} ]$: Projected angular separation between planet and star on the celestial sphere.
- **`pl_nespec`**, **`pl_ntranspec`**, **`pl_ndispec`**: Number of available emission, transmission, and direct-imaging spectra.
- **`pl_pubdate`**: Reference publication date for planet parameters (YYYY-MM).

---

## 2. Host-Star Properties (`domain: star`)

- **`hostname`**: Primary designation of the host star.
- **`hd_name`**, **`hip_name`**, **`tic_id`**, **`gaia_dr2_id`**, **`gaia_dr3_id`**: Cross-match catalog identifiers from the Henry Draper, Hipparcos, TESS Input Catalog (TIC), and Gaia DR2/DR3 catalogs.
- **`st_spectype`**: Morgan-Keenan spectral classification (e.g., `G2V` for Solar-type, `M3.5V` for Red Dwarf, `K1IV` for Subgiant).
- **`st_teff`** $[ \text{K} ]$: Stellar effective photospheric temperature (Sun is $5772\text{ K}$).
- **`st_rad`** $[ R_\odot ]$: Stellar radius in solar radii ($1\, R_\odot = 695,700\text{ km}$).
- **`st_mass`** $[ M_\odot ]$: Stellar mass in solar masses ($1\, M_\odot = 1.98847 \times 10^{30}\text{ kg}$).
- **`st_met`** $[ \text{dex} ]$: Metallicity $[ \text{Fe/H} ]$ — logarithmic ratio of iron abundance relative to the Sun ($0.0 = \text{Solar}$, $+0.3 = \text{twice Solar}$, $-0.3 = \text{half Solar}$).
- **`st_logg`** $[ \log_{10}(\text{cm/s}^2) ]$: Surface gravity in logarithmic cgs units (Sun $\approx 4.44$).
- **`st_lum`** $[ \log_{10}(L_\odot) ]$: Bolometric luminosity in logarithmic solar units.
- **`st_age`** $[ \text{Gyr} ]$: Estimated stellar age in billions of years (Universe $\approx 13.8\text{ Gyr}$, Sun $\approx 4.6\text{ Gyr}$).
- **`st_dens`** $[ \text{g/cm}^3 ]$: Mean bulk stellar density.
- **`st_rotp`** $[ \text{days} ]$: Stellar rotational period at the equator.
- **`st_vsin`** $[ \text{km/s} ]$: Projected rotational velocity ($v \sin i_\star$).
- **`st_radv`** $[ \text{km/s} ]$: Systemic heliocentric radial velocity of the host star.
- **`st_log_rhk`** $[ \text{dex} ]$: Chromospheric magnetic activity index $\log R'_{HK}$ measured from Ca II H & K lines.
- **`st_nphot`**, **`st_nrvc`**, **`st_nspec`**: Number of available photometric, radial velocity, and spectroscopic datasets.

---

## 3. Planetary System Properties (`domain: system`)

- **`sy_name`**: System name identifier.
- **`ra`** $[ \text{degrees} ]$: Right Ascension in decimal degrees (ICRS J2000.0 coordinate frame).
- **`dec`** $[ \text{degrees} ]$: Declination in decimal degrees (ICRS J2000.0 coordinate frame).
- **`sy_dist`** $[ \text{pc} ]$: Distance to the system in parsecs ($1\text{ pc} \approx 3.26\text{ light-years} \approx 3.086 \times 10^{13}\text{ km}$).
- **`sy_plx`** $[ \text{mas} ]$: Trigonometric parallax in milliarcseconds ($d = 1000 / \varpi$).
- **`sy_pm`**, **`sy_pmra`**, **`sy_pmdec`** $[ \text{mas/yr} ]$: Total proper motion and components across the sky.
- **`sy_snum`**: Number of stars in the system ($1 = \text{single star}$, $2 = \text{binary}$, $3 = \text{triple}$, etc.).
- **`sy_pnum`**: Number of confirmed exoplanets in the system.
- **`sy_mnum`**: Number of confirmed moons in the system.
- **`cb_flag`**: Circumbinary flag ($1 = \text{circumbinary orbit around two stars}$; $0 = \text{orbiting single star}$).

### Multi-band Apparent Magnitudes ($m$)
Photometric magnitudes in standard astronomical filters (smaller/more negative numbers indicate brighter stars):
- **`sy_vmag`**: Johnson V-band ($\sim 550\text{ nm}$, green/visual optical).
- **`sy_bmag`**: Johnson B-band ($\sim 440\text{ nm}$, blue optical).
- **`sy_gaiamag`**: Gaia G-band ($\sim 330\text{--}1050\text{ nm}$, broad optical).
- **`sy_tmag`**: TESS red-optical/near-IR bandpass ($\sim 600\text{--}1000\text{ nm}$).
- **`sy_kepmag`**: Kepler broad optical bandpass ($\sim 420\text{--}900\text{ nm}$).
- **`sy_jmag`**, **`sy_hmag`**, **`sy_kmag`**: 2MASS Near-Infrared bands ($1.25\,\mu\text{m}$, $1.65\,\mu\text{m}$, $2.16\,\mu\text{m}$).
- **`sy_umag`**, **`sy_rmag`**, **`sy_imag`**, **`sy_zmag`**: SDSS Optical/NIR survey filters.
- **`sy_w1mag`**, **`sy_w2mag`**, **`sy_w3mag`**, **`sy_w4mag`**: WISE Mid-Infrared bands ($3.4\,\mu\text{m}$, $4.6\,\mu\text{m}$, $12\,\mu\text{m}$, $22\,\mu\text{m}$).

---

## 4. Discovery Properties (`domain: discovery`)

- **`discoverymethod`**: Primary detection method:
  - *Transit*: Periodic dipping in stellar flux.
  - *Radial Velocity*: Doppler shift of stellar absorption lines.
  - *Microlensing*: Gravitational lensing amplification of background light.
  - *Direct Imaging*: Direct spatial resolution of planetary photons.
  - *Transit Timing Variations (TTV)*: Gravitational perturbations in transit schedules.
  - *Eclipse Timing Variations (ETV)* / *Pulsar Timing / Astrometry*.
- **`disc_year`**: Year of confirmed discovery publication.
- **`disc_facility`**: Primary observatory or space telescope (e.g., *Kepler*, *TESS*, *Hubble Space Telescope*, *W. M. Keck Observatory*, *La Silla Observatory*, *CoRoT*, *JWST*).
- **`disc_instrument`**: Specific spectrograph or photometer (e.g., *HARPS*, *ESPRESSO*, *HIRES*, *Kepler Photometer*).
- **`disc_locale`**: Operating environment: `Space` or `Ground`.
- **`disc_pubdate`**: Discovery announcement date (YYYY-MM).
- **`disc_refname`**: ADS bibliography reference tag.

---

## 5. Derived Properties & Classifications

The Stage 1 pipeline computes three derived fields for downstream modeling and visualization:

### 1. `planet_class` (Morphological Classification)
Categorized based on measured radius ($R_p$) or mass ($M_p$):
- **Terrestrial / Rocky**: $R_p < 1.25\, R_\oplus$ (or $M_p < 2.0\, M_\oplus$)
- **Super-Earth**: $1.25 \le R_p < 2.0\, R_\oplus$ (or $2.0 \le M_p < 10.0\, M_\oplus$)
- **Sub-Neptune / Mini-Neptune**: $2.0 \le R_p < 4.0\, R_\oplus$
- **Neptune-like**: $4.0 \le R_p < 6.0\, R_\oplus$ (or $10.0 \le M_p < 50.0\, M_\oplus$)
- **Gas Giant / Jovian**: $R_p \ge 6.0\, R_\oplus$ (or $M_p \ge 50.0\, M_\oplus$)
- **Unknown**: Insufficient physical parameter constraints.

### 2. `habitability_zone_est` (Insolation Regime)
Based on Kopparapu et al. stellar insolation models relative to Earth solar flux ($S_{\text{eff}} = F / F_\oplus$):
- **Conservative Habitable Zone**: $0.35 \le S_{\text{eff}} \le 1.11$ (Runaway Greenhouse to Maximum Greenhouse limits).
- **Optimistic Habitable Zone**: $0.32 \le S_{\text{eff}} < 0.35$ or $1.11 < S_{\text{eff}} \le 1.78$ (Early Mars to Recent Venus limits).
- **Hot Zone**: $S_{\text{eff}} > 1.78$ (Planets interior to the habitable zone).
- **Cold Zone**: $S_{\text{eff}} < 0.32$ (Planets exterior to the habitable zone).
- **Unknown**: Insufficient insolation or temperature data.

### 3. `calc_density` $[ \text{g/cm}^3 ]$
Calculated bulk density estimated from mass and radius when archive empirical density (`pl_dens`) is unpopulated:
$$\rho = 5.514 \times \frac{M / M_\oplus}{(R / R_\oplus)^3}\text{ g/cm}^3$$

