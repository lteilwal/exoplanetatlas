# ExoPlanet Atlas: Complete Codebase Learning Manual & Data Architecture Guide

> **How to use this manual:** Open this guide on the left side of your VS Code workspace, and open the referenced source files on the right side. Follow the controlled sequence from Stage 1 data engineering to database normalization, FastAPI service layers, minimal Plain CSS frontend rendering, and Gemini + Model Context Protocol (MCP) AI integration.

---

# TABLE OF CONTENTS

1. [Project Overview & End-to-End Mental Model](#1-project-overview--end-to-end-mental-model)
2. [Scientific Data Dictionary & Parameter Lifecycle](#2-scientific-data-dictionary--parameter-lifecycle)
3. [Stage 1 — Data Acquisition & Processing Pipeline](#3-stage-1--data-acquisition--processing-pipeline)
4. [Stage 2 — Database Models & Schema Design](#4-stage-2--database-models--schema-design)
5. [Stage 2 — Database Ingestion & Transactional Integrity](#5-stage-2--database-ingestion--transactional-integrity)
6. [Stage 2 — Database Migrations (Alembic)](#6-stage-2--database-migrations-alembic)
7. [Stage 2 — Service Layer & Dynamic Query Construction](#7-stage-2--service-layer--dynamic-query-construction)
8. [Stage 2 — FastAPI REST Application & Dependency Injection](#8-stage-2--fastapi-rest-application--dependency-injection)
9. [Stage 2 — Pydantic Schemas & DTO Serialization](#9-stage-2--pydantic-schemas--dto-serialization)
10. [Stage 3 — Frontend Architecture (React + TypeScript + Plain CSS)](#10-stage-3--frontend-architecture-react--typescript--plain-css)
11. [Stage 3 — Data Flow: From API Response to UI State](#11-stage-3--data-flow-from-api-response-to-ui-state)
12. [Stage 3 — Mathematical Scientific Visualizations](#12-stage-3--mathematical-scientific-visualizations)
13. [AI Layer — Grounded Narrative Synthesis & Archival Q&A](#13-ai-layer--grounded-narrative-synthesis--archival-qa)
14. [MCP Layer — Model Context Protocol Server & Tool Execution](#14-mcp-layer--model-context-protocol-server--tool-execution)
15. [Automated Testing Suite (50 Tests)](#15-automated-testing-suite-50-tests)
16. [Running, Deploying, and Ports Architecture](#16-running-deploying-and-ports-architecture)
17. [Practical Debugging Manual](#17-practical-debugging-manual)
18. [Complete End-to-End Data Trace: TRAPPIST-1 e](#18-complete-end-to-end-data-trace-trappist-1-e)
19. [How to Modify and Extend the Codebase](#19-how-to-modify-and-extend-the-codebase)
20. [Structured Learning Plan & Practical Exercises](#20-structured-learning-plan--practical-exercises)

---

# 1. PROJECT OVERVIEW & END-TO-END MENTAL MODEL

### 1.1 Purpose of the Project
The **ExoPlanet Atlas** is an end-to-end scientific data platform that acquires, normalizes, stores, queries, visualizes, and interrogates confirmed exoplanet data from the NASA Exoplanet Archive.

It is structured into three clean, decoupled stages:
1. **Stage 1 (Data Engineering)**: Pulls data via the Table Access Protocol (TAP API), validates physical parameters, derives astrophysical features (density, morphology, habitable zone boundaries), and produces a clean dataset.
2. **Stage 2 (Relational Backend)**: Normalizes the flat dataset into Third Normal Form (3NF) relational tables (`systems`, `stars`, `planets`, `discoveries`), manages DDL migrations via Alembic, executes queries through SQLAlchemy 2.0 services, and exposes a high-performance REST API with FastAPI and Pydantic v2.
3. **Stage 3 (Scientific Presentation & AI)**: Renders a minimal, zero-bloat Plain CSS research terminal in React 18 + TypeScript with 2D geometric SVG orbit diagrams, and mediates natural-language inquiry through **Gemini** using a **Model Context Protocol (MCP)** server that enforces strict database grounding.

```
========================================================================================================
                                      EXOPLANET ATLAS DATA LIFECYCLE
========================================================================================================

  [ NASA IPAC EXOPLANET ARCHIVE ]
                 │  HTTP GET / TAP ADQL Query (`pscomppars` composite table)
                 ▼
  [ STAGE 1: INGESTION & PIPELINE ]
    • `src/tap_client.py`      ──► Fetches synchronous CSV text via Table Access Protocol
    • `src/schema.py`          ──► Curates 50+ mandatory astronomical column definitions
    • `src/processing.py`      ──► Enforces physical bounds; computes Density, Classes, HZ
    • `src/pipeline.py`        ──► Orchestrates workflow; produces `data/processed/exoplanets_processed.csv`
                 │
                 ▼
  [ STAGE 2: RELATIONAL DATABASE & BACKEND ]
    • `src/models/`            ──► 3NF Normalized ORM models (`systems`, `stars`, `planets`, `discoveries`)
    • `alembic/`               ──► Version-controlled schema migrations (`001_initial_schema.py`)
    • `src/services/ingestion` ──► Single-transaction bulk loader (`load_database.py`)
    • `src/services/*_service` ──► SQLAlchemy queries with eager joined loads (`joinedload`)
    • `src/api/v1/`            ──► FastAPI routers with pagination, multi-param filters, CORS
                 │
                 ├───────────────────────────────────────────────────────┐
                 │ HTTP REST (/api/v1/planets, /systems, /stats)         │ Tool Calls
                 ▼                                                       ▼
  [ STAGE 3: SCIENTIFIC TERMINAL ]                         [ STAGE 3: AI & MCP LAYER ]
    • `frontend/src/pages/`     ──► Catalog, Detail, System  • `src/mcp/server.py`
    • `frontend/src/components/`──► OrbitDiagram (SVG Math)    (Exposes read-only DB tools)
    • `frontend/src/index.css`  ──► Pure Plain CSS terminal    • `src/services/ai_service.py`
                                                               (Gemini 2.5 Flash + MCP Grounding)
========================================================================================================
```

---

# 2. SCIENTIFIC DATA DICTIONARY & PARAMETER LIFECYCLE

Below is the complete lifecycle of every critical astronomical parameter handled by the codebase.

| Parameter | Symbol / Unit | Origin / Type | Stage 1 Transform (`processing.py`) | Database Column (`models/`) | API Schema (`schemas/`) | UI Location (`PlanetDetailPage`) | Astrophysical Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Planet Radius** | $R_\oplus$ (Earth Radii) | Observed (Transit depth $\Delta F/F \approx (R_p/R_*)^2$) | Filtered $R_p \in [0.1, 100.0]$ | `planets.radius_earth` | `PlanetSummary.radius_earth` | Top metric card, Scale diagram | Physical radius relative to Earth ($1 R_\oplus = 6,371\text{ km}$). |
| **Planet Mass** | $M_\oplus$ (Earth Masses) | Observed (Radial velocity wobble $K$ or Transit Timing) | Filtered $M_p \in [0.01, 100000.0]$ | `planets.mass_earth` | `PlanetSummary.mass_earth` | Top metric card | Total mass relative to Earth ($1 M_\oplus = 5.972 \times 10^{24}\text{ kg}$). |
| **Mean Density** | $\text{g/cm}^3$ | **Derived** ($\rho = \frac{M}{4/3 \pi R^3}$) | Computed via $\rho = 5.515 \cdot \frac{M/M_\oplus}{(R/R_\oplus)^3}$ | `planets.density_g_cm3` | `PlanetDetail.density_g_cm3` | Planetary Physical Properties | Informs internal composition (iron, silicate rock, water ocean, gas envelope). |
| **Orbital Period** | Days | Observed (Light curve periodicity / RV period) | Filtered $P > 0.01\text{ d}$ | `planets.orbital_period_days` | `PlanetSummary.orbital_period_days` | Metric card & Orbit diagram | Time required for one complete revolution around host star. |
| **Semi-Major Axis** | $\text{AU}$ (Astronomical Units) | Derived (Kepler's 3rd Law $a^3 \propto M_* P^2$) or Transit fit | Filtered $a > 0.0001\text{ AU}$ | `planets.semi_major_axis_au` | `PlanetDetail.semi_major_axis_au` | Orbit diagram geometry scale | Mean orbital distance ($1\text{ AU} \approx 1.496 \times 10^8\text{ km}$). |
| **Orbital Eccentricity**| Dimensionless $[0, 1)$ | Observed (RV curve shape / Transit duration) | Filtered $e \in [0, 1.0)$ | `planets.eccentricity` | `PlanetDetail.eccentricity` | Orbit diagram geometry shape | Deviation of orbit from a perfect circle ($e=0$: circular, $e\to 1$: highly elliptical). |
| **Equilibrium Temp** | Kelvin ($\text{K}$) | Calculated ($T_{\text{eq}} = T_* (R_*/2a)^{1/2} (1-A)^{1/4}$) | Filtered $T_{\text{eq}} \in [10, 10000\text{ K}]$ | `planets.equilibrium_temp_k` | `PlanetSummary.equilibrium_temp_k` | Metric card & Thermal section | Theoretical blackbody temperature assuming uniform thermal redistribution. |
| **Habitability Zone** | Category String | **Derived** (Kopparapu et al. flux model) | Classified based on $r_{\text{inner}}=\sqrt{L_*/1.1}$ and $r_{\text{outer}}=\sqrt{L_*/0.53}$ | `planets.habitability_zone_est`| `PlanetSummary.habitability_zone_est` | HZ badge & Orbit diagram ring | Regime estimating whether liquid surface water could remain stable. |
| **Morphology Class** | Category String | **Derived** (Radius regime criteria) | Classified into Terrestrial, Super-Earth, Sub-Neptune, Neptune-like, Gas Giant | `planets.planet_class` | `PlanetSummary.planet_class` | Header badge, filters | Structural category defining geological vs gaseous nature. |
| **Stellar Temp ($T_{\text{eff}}$)**| Kelvin ($\text{K}$) | Observed (Spectroscopy / Color photometry) | Filtered $T_{\text{eff}} \in [500, 50000\text{ K}]$ | `stars.effective_temp_k` | `StarSummary.effective_temp_k` | Host Star Properties card | Photospheric surface temperature of host star ($T_{\odot} \approx 5778\text{ K}$). |
| **Distance** | Parsecs ($\text{pc}$) | Observed (Gaia astrometric parallax $\varpi$, $d=1/\varpi$) | Filtered $d \in [0.1, 100000\text{ pc}]$ | `systems.distance_pc` | `SystemSummary.distance_pc` | Header subtitle, System card | Distance from Earth ($1\text{ pc} \approx 3.26\text{ light-years}$). |

---

# 3. STAGE 1 — DATA ACQUISITION AND PROCESSING

Stage 1 is responsible for retrieving authoritative observational records from NASA IPAC and preparing a mathematically consistent, validated dataset.

```
┌─────────────────────────┐
│ NASA TAP API (HTTP GET) │
└────────────┬────────────┘
             │ `src/tap_client.py` (ADQL Query over `pscomppars`)
             ▼
┌─────────────────────────┐
│ Raw CSV Data            │
└────────────┬────────────┘
             │ `src/schema.py` (Curated Column Dictionary)
             ▼
┌─────────────────────────┐
│ Processing Pipeline     │ ──► `src/processing.py`
│ - Strip null sentinels  │     - Density calculation
│ - Validate bounds       │     - Kopparapu Habitable Zone model
│ - Feature engineering   │     - Radius Morphology classifier
└────────────┬────────────┘
             │ `src/pipeline.py`
             ▼
┌───────────────────────────────────────────────┐
│ Cleaned Artifact: `exoplanets_processed.csv`  │ (6,354 rows)
└───────────────────────────────────────────────┘
```

---

### `src/tap_client.py`

**Purpose**: Implements an HTTP client communicating with Caltech's IPAC TAP (Table Access Protocol) service using Astronomical Data Query Language (ADQL).

> **Open this file now**: `src/tap_client.py`

**Read these functions first:**
1. `build_curated_query()` (Line 50)
2. `fetch_exoplanets_csv()` (Line 80)
3. `query_to_dataframe()` (Line 118)

**Before reading this file, understand:**
- TAP is the IVOA (International Virtual Observatory Alliance) standard protocol for querying astronomical tables via HTTP.
- ADQL is an astronomical dialect of SQL92.
- The table `pscomppars` (Planetary Systems Composite Parameters) is NASA's single authoritative composite table containing one consolidated row per confirmed planet.

**While reading it, pay attention to:**
- How `TAP_BASE_URL` (`https://exoplanetarchive.ipac.caltech.edu/TAP/sync`) handles synchronous queries.
- How `fetch_exoplanets_csv()` checks for HTTP errors and inspects whether the HTTP 200 payload actually contains a TAP XML `<INFO name="QUERY_STATUS" value="ERROR"/>` error envelope.

**After reading it, you should be able to explain:**
- Why the query targets `pscomppars` instead of the raw multi-row observations table `ps`.
- What happens if the NASA TAP server rejects an invalid column name.

---

### `src/processing.py`

**Purpose**: Performs numerical validation, eliminates unphysical outliers, and executes astrophysical feature engineering.

> **Open this file now**: `src/processing.py`

**Read these functions first:**
1. `compute_derived_features()` (Line 130)
2. `classify_planet_radius()` (Line 75)
3. `calculate_habitable_zone()` (Line 95)
4. `filter_and_validate()` (Line 180)
5. `clean_dataframe()` (Line 230)

**Mathematical Formulations in this File:**
1. **Bulk Planetary Density**:
   $$\rho = \frac{M_p}{\frac{4}{3} \pi R_p^3} \implies \rho \left[\text{g/cm}^3\right] = 5.515 \cdot \frac{M_p / M_\oplus}{(R_p / R_\oplus)^3}$$
2. **Main-Sequence Stellar Luminosity**:
   $$L_* \approx \left(\frac{M_*}{M_\odot}\right)^{3.5} L_\odot$$
3. **Kopparapu et al. Habitable Zone Boundaries**:
   $$r_{\text{inner}} = \sqrt{\frac{L_*}{1.1}} \text{ [AU]}, \quad r_{\text{outer}} = \sqrt{\frac{L_*}{0.53}} \text{ [AU]}$$
4. **Morphological Classification**:
   - $R_p < 1.25 R_\oplus$: `Terrestrial`
   - $1.25 R_\oplus \le R_p < 2.0 R_\oplus$: `Super-Earth`
   - $2.0 R_\oplus \le R_p < 4.0 R_\oplus$: `Sub-Neptune`
   - $4.0 R_\oplus \le R_p < 6.0 R_\oplus$: `Neptune-like`
   - $R_p \ge 6.0 R_\oplus$: `Gas Giant`

**After reading it, you should be able to explain:**
- Why unphysical measurements (e.g. negative orbital period or negative stellar mass) are converted to `NaN` (SQL `NULL`) rather than dropping the whole planet record.

---

# 4. STAGE 2 — DATABASE MODELS & SCHEMA DESIGN

Stage 2 normalizes the flat dataset into a 3NF relational schema that guarantees referential integrity, eliminates redundancy, and enables efficient joined queries.

```
┌────────────────────────────────────────────────────────┐
│                        SYSTEMS                         │
│  PK: id (INTEGER)                                      │
│  UQ: name (VARCHAR 128)                                │
│      distance_pc, ra, dec, star_count, planet_count    │
│      v_mag, gaia_mag, tess_mag, kepler_mag             │
└───────────┬────────────────────────────────┬───────────┘
            │ 1-to-Many                      │ 1-to-Many
            ▼                                ▼
┌──────────────────────────────┐ ┌───────────────────────┐
│            STARS             │ │        PLANETS        │
│  PK: id (INTEGER)            │ │  PK: id (INTEGER)     │
│  FK: system_id ──► systems.id│ │  FK: system_id ───────┤
│  UQ: name (VARCHAR 128)      │ │  FK: star_id ─────────┤
│      spectral_type, teff     │ │  UQ: name (VARCHAR)   │
│      mass_solar, radius_solar│ │      radius_earth     │
│      metallicity             │ │      mass_earth       │
└───────────┬──────────────────┘ │      orbital_period   │
            │                    │      semi_major_axis  │
            │ 1-to-Many          │      eccentricity     │
            └───────────────────►│      equilibrium_temp │
                                 │      planet_class     │
                                 │      habitable_zone   │
                                 └───────────┬───────────┘
                                             │ 1-to-1
                                             ▼
                                 ┌───────────────────────┐
                                 │      DISCOVERIES      │
                                 │  PK: id (INTEGER)     │
                                 │  FK: planet_id (UQ)   │
                                 │      discovery_method │
                                 │      discovery_year   │
                                 │      discovery_facility
                                 └───────────────────────┘
```

---

### `src/models/`

> **Open these files now**:
> 1. `src/models/system.py`
> 2. `src/models/star.py`
> 3. `src/models/planet.py`
> 4. `src/models/discovery.py`

**Key Relationship Mechanics:**
- **Foreign Key Constraints**: `planets.system_id` references `systems.id` with `ondelete="CASCADE"`.
- **Bidirectional ORM Relationships**:
  - In `Planet`: `system = relationship("System", back_populates="planets")`
  - In `System`: `planets = relationship("Planet", back_populates="system", cascade="all, delete-orphan")`
- **1-to-1 Unique Constraint**: In `Discovery`, `planet_id = Column(Integer, ForeignKey("planets.id", ondelete="CASCADE"), unique=True, nullable=False)`.

**Database Indexing Strategy:**
- In `Planet`: `Index("ix_planets_class_hz", "planet_class", "habitability_zone_est")` enables instantaneous catalog filtering by morphology and habitability.
- In `System` & `Star`: Unique indexes on `name` allow $O(1)$ lookups during bulk ingestion.

---

# 5. STAGE 2 — DATABASE INGESTION & TRANSACTIONAL INTEGRITY

### `src/services/ingestion.py`

**Purpose**: Ingests the 6,354 processed CSV records into the normalized database in a single, atomic, idempotent transaction.

> **Open this file now**: `src/services/ingestion.py`

**Read these functions first:**
1. `ingest_csv_to_database()` (Line 65)
2. `_extract_system_data()` (Line 210)
3. `_extract_star_data()` (Line 235)
4. `_extract_planet_data()` (Line 260)
5. `_extract_discovery_data()` (Line 285)

**How Ingestion Avoids Duplication:**
During ingestion, multiple planets belong to the same system (e.g. TRAPPIST-1 b through h belong to system TRAPPIST-1).
1. `ingest_csv_to_database()` maintains in-memory lookup caches: `systems_cache = {}` and `stars_cache = {}`.
2. When row $N$ is processed, it checks if `system_name` exists in `systems_cache`. If not, a new `System` ORM instance is instantiated, added to the session, flushed (`db.flush()`) to acquire its generated surrogate PK (`system.id`), and cached.
3. The `Planet` instance is then constructed referencing the verified `system_id` and `star_id`.
4. All 6,354 planets and their associated entities are committed in a single transaction (`db.commit()`). If any row violates constraints, the entire batch rolls back (`db.rollback()`), guaranteeing zero corrupted partial state.

---

# 6. STAGE 2 — DATABASE MIGRATIONS (ALEMBIC)

### `alembic/` & `alembic.ini`

**Purpose**: Manages programmatic, version-controlled Data Definition Language (DDL) migrations.

```
Alembic CLI / Script ──► `alembic/env.py` ──► `src/db/base.py` (Base.metadata) ──► `alembic/versions/` ──► PostgreSQL DDL
```

> **Open this file now**: `alembic/versions/001_initial_schema.py`

**Why Migrations Are Essential:**
Modifying a Python class in `src/models/planet.py` (such as adding a new column) does **not** alter existing tables in PostgreSQL. Alembic creates reversible migration scripts:
- `upgrade()`: Executes `op.create_table(...)` and `op.create_index(...)`.
- `downgrade()`: Executes `op.drop_table(...)` and `op.drop_index(...)` in reverse dependency order.

---

# 7. STAGE 2 — SERVICE LAYER & DYNAMIC QUERY CONSTRUCTION

The service layer encapsulates business logic, filtering, counting, and eager joined loads.

> **Open this file now**: `src/services/planet_service.py`

### Line-by-Line Query Analysis: `get_planets()`

```python
# 1. Base Query with Eager Joined Loads (Solves N+1 Query Problem)
query = (
    select(Planet)
    .outerjoin(Planet.discovery)
    .outerjoin(Planet.system)
    .outerjoin(Planet.star)
    .options(
        joinedload(Planet.discovery),
        joinedload(Planet.system),
        joinedload(Planet.star),
    )
)

# 2. Multi-Column Substring Search across Planet, Host Star, and System
if search:
    search_pattern = f"%{search.strip()}%"
    query = query.where(
        or_(
            Planet.name.ilike(search_pattern),
            Star.name.ilike(search_pattern),
            System.name.ilike(search_pattern),
        )
    )

# 3. Dynamic Range and Categorical Filtering
if planet_class:
    query = query.where(Planet.planet_class == planet_class)
if min_radius_earth is not None:
    query = query.where(Planet.radius_earth >= min_radius_earth)

# 4. Filtered Total Count Calculation (Executes Subquery Count)
count_query = select(func.count()).select_from(query.subquery())
total_items = db.scalar(count_query) or 0

# 5. Dynamic Sorting with Nulls Last
sort_col = sort_map.get(sort_by.lower(), Planet.name)
if order.lower() == "desc":
    query = query.order_by(sort_col.desc().nullslast(), Planet.name.asc())
else:
    query = query.order_by(sort_col.asc().nullslast(), Planet.name.asc())

# 6. Offset Pagination
offset = (page - 1) * page_size
query = query.offset(offset).limit(page_size)
items = list(db.scalars(query).unique().all())
```

**Why this is optimal:**
- Using `joinedload(...)` retrieves the planet and its nested host star, system, and discovery in a **single SQL JOIN statement** instead of executing 1 + $3N$ separate SQL queries.

---

# 8. STAGE 2 — FASTAPI REST APPLICATION & DEPENDENCY INJECTION

### `src/main.py` & `src/api/v1/`

**Request Lifecycle Trace:**

```
HTTP GET /api/v1/planets?search=Kepler&page=1
  │
  ▼
FastAPI Routing (`src/api/v1/planets.py`: `list_planets()`)
  │ Validates Query Parameters via Pydantic
  ▼
Dependency Injection (`src/api/deps.py`: `get_db()`)
  │ Yields scoped SQLAlchemy `Session` from `SessionLocal()`
  ▼
Service Layer (`src/services/planet_service.py`: `get_planets()`)
  │ Executes SQL SELECT query on PostgreSQL / SQLite
  ▼
ORM Entity Instances (`List[Planet]`)
  │ Serialized into Pydantic DTOs (`PaginatedResponse[PlanetSummary]`)
  ▼
HTTP 200 OK + Clean JSON Response Payload
```

---

# 9. STAGE 2 — PYDANTIC SCHEMAS & DTO SERIALIZATION

### `src/schemas/`

> **Open this file now**: `src/schemas/planet.py`

**Why Separate Schemas Exist:**
- `PlanetSummary`: Compact schema for catalog grid/tables (reduces JSON payload from 2.5 KB to 300 bytes per planet).
- `PlanetDetail`: Comprehensive schema for the planetary dossier page (includes nested `StarSummary`, `SystemSummary`, and `Discovery`).
- `from_attributes = True` (`orm_mode`): Instructs Pydantic to read attributes directly from SQLAlchemy ORM objects.

---

# 10. STAGE 3 — FRONTEND ARCHITECTURE (REACT + TYPESCRIPT + PLAIN CSS)

The frontend is a focused scientific research terminal built with **React 18**, **TypeScript 5**, **Vite 6**, and pure **Plain CSS**.

```
frontend/src/
├── main.tsx              ──► Application entrypoint; mounts React DOM
├── App.tsx               ──► Native Hash Router & Navigation header
├── index.css             ──► 11.9 kB Plain CSS (Design system, custom properties)
├── api/
│   └── client.ts         ──► Typed fetch HTTP client wrapper
├── types/
│   └── index.ts          ──► TypeScript interfaces matching backend Pydantic DTOs
├── components/
│   ├── CatalogFilterBar.tsx  ──► Multi-parameter range sliders, category presets, search bar
│   ├── Footer.tsx            ──► Minimal terminal status and citation footer
│   ├── MetricCard.tsx        ──► High-density telemetry value display
│   ├── Navbar.tsx            ──► Terminal header & hash navigation
│   ├── OrbitDiagram.tsx      ──► Interactive 2D SVG orbital geometry with zoom/pan
│   ├── Pagination.tsx        ──► Page offset and limit controller
│   ├── PlanetCard.tsx        ──► High-density telemetry card
│   ├── PlanetTable.tsx       ──► Dense tabular view with clickable column sorting
│   ├── ScaleDiagram.tsx      ──► Physical radius comparison diagram (Earth & Jupiter baselines)
│   └── SystemArchitectureDiagram.tsx ──► Sibling planet multi-orbit visualization
└── pages/
    ├── CatalogPage.tsx       ──► Searchable catalog (Grid & Table views)
    ├── ComparePage.tsx       ──► Side-by-side comparison matrix (2 to 4 worlds)
    ├── ExplorePage.tsx       ──► Curated exploration & extremes showcase
    ├── PlanetDetailPage.tsx  ──► Full planetary dossier, orbit viewer, AI Q&A
    ├── SystemDetailPage.tsx  ──► Multi-planet sibling architecture view
    └── SystemsListPage.tsx   ──► Planetary systems directory
```

---

# 11. STAGE 3 — DATA FLOW: FROM API RESPONSE TO UI STATE

### 1. Catalog Filtering Flow:
```
User clicks "Habitable Zone" preset in `CatalogFilterBar.tsx`
  ──► State updates: `setFilters(prev => ({ ...prev, habitability_zone_est: 'Conservative Habitable Zone' }))`
  ──► `useEffect` triggers `loadData()` in `CatalogPage.tsx`
  ──► `api.getPlanets(filters)` executes `fetch('/api/v1/planets?...')`
  ──► Backend returns `{ items: [...], total: 72, page: 1, total_pages: 3 }`
  ──► React updates `planets` state ──► Grid re-renders 72 habitable worlds.
```

### 2. Client-Side Hash Routing Flow:
- `App.tsx` listens to `window.location.hash` changes (`#planet/TRAPPIST-1%20e`, `#system/Kepler-11`, `#compare`).
- Zero external routing libraries: prevents routing library churn and guarantees instant, zero-latency navigation.

---

# 12. STAGE 3 — MATHEMATICAL SCIENTIFIC VISUALIZATIONS

### `frontend/src/components/OrbitDiagram.tsx`

> **Open this file now**: `frontend/src/components/OrbitDiagram.tsx`

**Mathematical Formulation:**
The orbit is rendered as a Keplerian ellipse in SVG coordinates:
1. **Semi-major axis ($a$)** & **Eccentricity ($e$)**:
   $$\text{Semi-minor axis: } b = a \sqrt{1 - e^2}$$
   $$\text{Focal distance from center: } c = a \cdot e$$
2. **Host Star Focal Offset**:
   In Keplerian orbits, the host star sits at **one focus**, not at the center. The SVG ellipse is rendered at $(c_x + c \cdot \text{scale}, c_y)$, placing the star precisely at $(c_x, c_y)$.
3. **Habitable Zone Annulus**:
   Rendered as concentric green circles showing $r_{\text{inner}}$ and $r_{\text{outer}}$, allowing instant visual verification of whether the planet's orbit intersects the habitable zone.
4. **Interactive Zoom & Pan Controls**:
   - Uses SVG transformation matrix `transform="translate(pan.x, pan.y) scale(zoom)"`.
   - Listens to mouse wheel delta (`e.deltaY`) for smooth scaling ($0.2\times$ to $8.0\times$).

---

# 13. AI LAYER — GROUNDED NARRATIVE SYNTHESIS & ARCHIVAL Q&A

### `src/services/ai_service.py`

**Purpose**: Uses **Gemini** (`gemini-2.5-flash`) to generate factual natural-language summaries and answer user questions, strictly constrained by database facts retrieved via MCP tools.

> **Open this file now**: `src/services/ai_service.py`

**Read these sections first:**
1. `DATABASE_SCHEMA_REFERENCE` (Line 38)
2. `SYSTEM_INSTRUCTION` (Line 95)
3. `generate_planet_summary_ai()` (Line 135)
4. `ask_planet_question_ai()` (Line 205)
5. `_answer_from_mcp_data()` (Line 320)

```
┌────────────────────────────────────────────────────────┐
│ User Inquiry: "What is the mass of TRAPPIST-1 e?"     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Gemini Client (`src/services/ai_service.py`)           │
│ - Injects Semantic Schema Reference & Strict Rules     │
│ - Issues Tool Call: `tool_get_planet("TRAPPIST-1 e")`  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Exoplanet MCP Server (`src/mcp/server.py`)             │
│ - Queries PostgreSQL via `planet_service`              │
│ - Returns verified JSON: `{"found": True, "mass_earth": 0.692, ...}`│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Gemini Synthesizes Grounded Answer:                    │
│ "TRAPPIST-1 e has a verified mass of 0.69 Earth masses.│
│ (MCP Tools Used: tool_get_planet)"                     │
└────────────────────────────────────────────────────────┘
```

#### 1. Gemini Semantic Schema Reference
Gemini is supplied with a concise semantic reference of the 4 normalized tables:
- `systems`: `name`, `distance_pc` (parsecs), `ra`, `dec` (deg), `star_count`, `planet_count`, `is_circumbinary`, multi-band magnitudes (`v_mag`, `gaia_mag`, `tess_mag`, `kepler_mag`).
- `stars`: `name`, `spectral_type` (Morgan-Keenan e.g. M1V, G2V), `effective_temp_k` (Kelvin), `mass_solar` ($M_\odot$), `radius_solar` ($R_\odot$), `metallicity` ([Fe/H] in dex).
- `planets`: `name`, `orbital_period_days` (days), `semi_major_axis_au` (AU), `eccentricity` ($e \in [0, 1)$), `inclination_deg` (deg), `radius_earth` ($R_\oplus$), `radius_jupiter` ($R_{\text{Jup}}$), `mass_earth` ($M_\oplus$), `mass_jupiter` ($M_{\text{Jup}}$), `equilibrium_temp_k` (K), `insolation_earth` ($S_\oplus$).
- `discoveries`: `discovery_method` (Transit, RV, Microlensing, Direct Imaging), `discovery_year`, `discovery_facility`.

#### 2. Catalogued vs. Derived Features
- **Catalogued Observational Data**: Direct archival measurements from telescope surveys.
- **ExoPlanet Atlas Derived Values**:
  - `density_g_cm3`: Calculated as $\rho = 5.515 \cdot (M_p/M_\oplus) / (R_p/R_\oplus)^3$.
  - `planet_class`: Morphological categorization based on radius (Terrestrial, Super-Earth, Sub-Neptune, Neptune-like, Gas Giant).
  - `habitability_zone_est`: Calculated from Kopparapu insolation flux boundaries.

#### 3. Strict Missing Data & No-Result Rules
- **Entity Not Found (`found: False`)**: Gemini explicitly informs the user that the entity does not exist in the database and suggests checking the astronomical designation.
- **Value Unavailable (`found: True`, field is `null`)**: If an entity exists but a specific measurement is unrecorded, Gemini explicitly states: *"According to archive records, this property has not been measured or is unconstrained for this object."* (Never substitutes zeros or guesses).
- **No SQL Execution**: Gemini is strictly prohibited from generating or executing raw SQL queries.

#### 4. Structured AI Logging
The AI service logs structured metrics using `logging.getLogger("exoplanet.ai")`:
- Query target, prompt preview, tools invoked, entity resolution status, and execution duration in milliseconds (`duration_ms`).

---

# 14. MCP LAYER — MODEL CONTEXT PROTOCOL SERVER & TOOL EXECUTION

### `src/mcp/server.py`

**Purpose**: Implements an official Model Context Protocol (MCP) server that exposes thin, controlled, read-only tools to LLMs without exposing raw SQL, connection strings, or database credentials.

> **Open this file now**: `src/mcp/server.py`

**Read these tool definitions:**
1. `tool_get_planet(name: str)` (Line 34)
2. `tool_get_system(name: str)` (Line 95)
3. `tool_get_star(name: str)` (Line 150)
4. `tool_search_planets(query, planet_class, habitability_zone, discovery_method, limit)` (Line 205)
5. `tool_compare_planets(planet_names)` (Line 260)

#### Architectural Invariant: Thin Mediation
```
Gemini ──► MCP Tool Call ──► SQLAlchemy Service Layer ──► PostgreSQL / SQLite
```
- The MCP server acts strictly as a **thin transport mediation layer**. It delegates 100% of database querying, filtering, and joins to the existing service layer (`planet_service.py` and `system_service.py`), eliminating code duplication.

#### Exposed MCP Tools & Signatures:
1. `tool_get_planet(name: str)`: Returns comprehensive planetary parameters (`radius_earth`, `mass_earth`, `density_g_cm3`, `orbital_period_days`, `equilibrium_temp_k`, `planet_class`, `habitability_zone_est`) and nested `star`, `system`, and `discovery` data. Returns `{"found": False, "message": "..."}` if not found.
2. `tool_get_system(name: str)`: Returns system multiplicity (`star_count`, `planet_count`), distance in parsecs, celestial coordinates (`ra`, `dec`), and lists of sibling `stars` and `planets`.
3. `tool_get_star(name: str)`: Returns stellar spectral type, effective temperature ($T_{\text{eff}}$), mass ($M_\odot$), radius ($R_\odot$), metallicity, and orbiting planets.
4. `tool_search_planets(query, planet_class, habitability_zone, discovery_method, limit)`: Filters confirmed exoplanets by name substring, morphological classification, habitability model, or detection method. Returns `{total_matches, returned_count, planets}`.
5. `tool_compare_planets(planet_names: list[str])`: Side-by-side comparative dictionary for up to 6 planets.

#### Structured MCP Logging
Tool calls are logged using `logging.getLogger("exoplanet.mcp")` with:
- `tool_name`, safe sanitized arguments, `found=True/False`, match counts, and execution latency (`duration_ms`). Zero sensitive credentials or tokens are ever logged.

---

# 15. AUTOMATED TESTING SUITE (50 TESTS)

The codebase includes **50 automated unit and integration tests** passing with 100% success in $<1.0\text{s}$:

```powershell
python -m unittest discover -s tests -v
```

### Test Suite Directory:
1. `tests/test_processing.py`: Tests physical bounds filtering, morphological classification, and density calculations.
2. `tests/test_schema.py`: Validates mandatory TAP column definitions and metadata serialization.
3. `tests/test_tap_client.py`: Verifies ADQL generation and TAP XML error envelope parsing.
4. `tests/test_pipeline.py`: Tests end-to-end pipeline execution with mocked TAP responses.
5. `tests/test_config.py`: Tests configuration paths, directories, and TAP constants.
6. `tests/test_models.py`: Tests ORM relationships and cascade deletions (`ON DELETE CASCADE`).
7. `tests/test_ingestion_service.py`: Verifies CSV ingestion, foreign key resolution, and deduplication.
8. `tests/test_migrations.py`: Runs full Alembic migration `upgrade()` and `downgrade()` cycles.
9. `tests/test_api_planets.py`: Tests pagination, substring search, filtering, and 404 handling.
10. `tests/test_api_systems.py`: Tests system hierarchies, star listings, and stats endpoints.
11. `tests/test_mcp_server.py`: Tests all 5 MCP database tools.
12. `tests/test_ai_service.py`: Tests Gemini narrative generation, grounded Q&A, and offline fallback handling.

---

# 16. RUNNING, DEPLOYING, AND PORTS ARCHITECTURE

### Local Execution Commands
```powershell
# 1. Ingest Data into Database
python load_database.py

# 2. Run All 50 Tests
python -m unittest discover -s tests -v

# 3. Start FastAPI Server (Port 8000)
python run_server.py

# 4. Start React Frontend (Port 3000)
cd frontend; npm run dev
```

### Port Mapping & Communication
- **Port 3000**: Vite Dev Server (Frontend).
- **Port 8000**: FastAPI Backend (REST API & MCP AI endpoints).
- **Port 5432**: PostgreSQL Database Container (Production).
- **Port 80**: Nginx Reverse Proxy (Production Docker stack).

---

# 17. PRACTICAL DEBUGGING MANUAL

| Symptom | Where to Look | What to Check | Likely Cause & Solution |
| :--- | :--- | :--- | :--- |
| **Database contains 0 planets** | `load_database.py` / `src/db/session.py` | Check if `data/processed/exoplanets_processed.csv` exists and is non-empty. | Run `python run_pipeline.py --from-raw` then `python load_database.py`. |
| **PostgreSQL Connection Failed** | `.env` / `src/core/config.py` | Look for `psycopg2.OperationalError: connection refused`. | Ensure PostgreSQL is running on port 5432 or allow SQLite fallback (`data/exoplanet.db`). |
| **FastAPI returns 404 for a planet** | `src/services/planet_service.py` | Check URL encoding in query (e.g. `TRAPPIST-1%20e`). | Ensure `identifier.strip()` matches `Planet.name.ilike(...)`. |
| **Frontend cannot fetch `/api`** | `frontend/vite.config.ts` | Verify proxy target is `http://127.0.0.1:8000`. | Ensure backend is running with `python run_server.py`. |
| **Gemini AI returns offline fallback**| `.env` | Verify `GEMINI_API_KEY` is present. | Add a valid Gemini API key in `.env` to enable online LLM reasoning. |

---

# 18. COMPLETE END-TO-END DATA TRACE: TRAPPIST-1 e

```
[ Step 1: NASA TAP Query ]
  ADQL Query selects: pl_name='TRAPPIST-1 e', pl_orbper=6.0996, pl_rade=0.920, pl_bmasse=0.692, st_teff=2566

[ Step 2: Stage 1 Processing ]
  - Bulk Density: ρ = 5.515 * (0.692) / (0.920^3) = 4.89 g/cm³
  - Morphology: Radius 0.92 R_E < 1.25 R_E ──► 'Terrestrial'
  - Habitable Zone: Semi-major axis a=0.029 AU is within [0.022, 0.032 AU] ──► 'Conservative Habitable Zone'
  - Written to `data/processed/exoplanets_processed.csv`

[ Step 3: Stage 2 Ingestion ]
  - Inserts `System` (name='TRAPPIST-1', distance=12.57 pc)
  - Inserts `Star` (name='TRAPPIST-1', spectral_type='M8V', Teff=2566 K)
  - Inserts `Planet` (name='TRAPPIST-1 e', radius=0.92, mass=0.69, period=6.10 d, Teq=251 K)
  - Inserts `Discovery` (method='Transit', year=2017, facility='La Silla Observatory')

[ Step 4: FastAPI & Service Layer ]
  - Request: `GET /api/v1/planets/TRAPPIST-1%20e`
  - `planet_service.get_planet_by_id_or_name()` executes joinedload SQL query.
  - Returns `PlanetDetail` JSON response.

[ Step 5: Frontend Presentation ]
  - Hash route: `/#planet/TRAPPIST-1%20e` mounts `PlanetDetailPage.tsx`.
  - `OrbitDiagram.tsx` renders 2D orbital ellipse inside the green Habitable Zone ring.
  - Gemini AI triggers `tool_get_planet("TRAPPIST-1 e")` via MCP server to synthesize the factual research dossier.
```

---

# 19. HOW TO MODIFY AND EXTEND THE CODEBASE

1. **Adding a New Derived Feature (e.g. Surface Gravity $g = M/R^2$)**:
   - In `src/processing.py`: Compute `df["surface_gravity_earth"] = df["mass_earth"] / (df["radius_earth"] ** 2)`.
   - In `src/models/planet.py`: Add `surface_gravity_earth = Column(Float, nullable=True)`.
   - Run `alembic revision --autogenerate -m "add surface gravity"` and `alembic upgrade head`.
   - In `src/schemas/planet.py`: Add field to `PlanetDetail`.
   - In `frontend/src/pages/PlanetDetailPage.tsx`: Render metric card.

2. **Adding a New MCP Database Tool**:
   - In `src/mcp/server.py`: Define `@mcp_server.tool() def get_extreme_planets() -> str: ...`.
   - In `src/services/ai_service.py`: Add function to `MCP_TOOLS` list.

---

# 20. STRUCTURED LEARNING PLAN & PRACTICAL EXERCISES

### 3-Day Mastery Plan

- **Session 1: Data Pipeline & Relational Models**
  - Read: `src/tap_client.py` $\to$ `src/processing.py` $\to$ `src/models/planet.py` $\to$ `src/services/ingestion.py`.
  - Exercise: Ingest the database and inspect tables using SQLite/PostgreSQL CLI.

- **Session 2: Services, FastAPI & Schemas**
  - Read: `src/services/planet_service.py` $\to$ `src/api/v1/planets.py` $\to$ `src/schemas/planet.py`.
  - Exercise: Add a new sorting parameter `density` to `get_planets()` and verify via Swagger UI.

- **Session 3: Frontend, Visualizations, MCP & AI**
  - Read: `frontend/src/components/OrbitDiagram.tsx` $\to$ `src/mcp/server.py` $\to$ `src/services/ai_service.py`.
  - Exercise: Add a sample question button to `PlanetDetailPage.tsx` and trace tool execution.

