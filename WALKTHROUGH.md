# ExoPlanet Atlas: Operations Walkthrough & System Overview

A complete operational guide for launching, deploying, and using the **ExoPlanet Atlas**, followed by a concise architectural overview of the scientific data pipeline, normalized database, FastAPI REST service, Gemini + MCP integration, and minimal Plain CSS frontend.

---

# PART 1: DETAILED WALKTHROUGH (LAUNCH, DEPLOY, USE)

---

## 1. Prerequisites

Ensure your system has the following installed:
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** & **npm**
- **Docker & Docker Compose** (optional, for production multi-container deployment)
- *(Optional)* **Gemini API Key**: If you wish to use live Gemini conversational synthesis (otherwise the application runs in deterministic offline MCP fallback mode with zero crashes).

---

## 2. Local Launch (Development Mode)

Follow these exact steps to run the complete stack locally on your machine.

### Step 1: Clone & Environment Setup
```powershell
# Navigate to the project root
cd c:\Comp\Python\SpaceProjects\ExoPlanet

# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Linux/macOS: source venv/bin/activate

# Install Python backend dependencies
pip install -e .
```

### Step 2: Configure Environment Variables
Copy the example `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env   # On Linux/macOS: cp .env.example .env
```
*(Optional)* Add your Gemini API key inside `.env`:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*Note: If PostgreSQL credentials are left at default and PostgreSQL is not running locally, the database engine automatically and seamlessly falls back to local SQLite at `data/exoplanet.db`.*

---

### Step 3: (Optional) Run Stage 1 Data Acquisition Pipeline
If you wish to refresh the dataset directly from the NASA Exoplanet Archive TAP API or re-run the cleaning pipeline:
```powershell
# Ingest and process from raw snapshot (fast: ~0.5s)
python run_pipeline.py --from-raw

# Or fetch live updates from Caltech/NASA TAP API
python run_pipeline.py
```
*Artifacts created: `data/processed/exoplanets_processed.csv` (6,354 planets), `data_dictionary.json`, and `exoplanets_metadata.json`.*

---

### Step 4: Run Stage 2 Database Ingestion
Initialize the relational database schema (Alembic migrations) and ingest all 6,354 planets across normalized tables:
```powershell
python load_database.py
```
*Output: Automatically creates tables (`systems`, `stars`, `planets`, `discoveries`) and ingests all records in ~10 seconds.*

---

### Step 5: Launch FastAPI REST Server
Start the backend Uvicorn server:
```powershell
python run_server.py
```
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc Technical Docs**: `http://127.0.0.1:8000/redoc`

---

### Step 6: Launch Minimal React Frontend
Open a second terminal window:
```powershell
cd frontend
npm install
npm run dev
```
- **Web Application**: `http://localhost:3000`
- The Vite dev server automatically proxies all `/api` requests to the FastAPI backend on port 8000.

---

## 3. Production Deployment (Docker Compose)

For production Linux servers, VPS, or cloud deployments, run the entire containerized multi-service stack with a single command:

```bash
docker compose up --build -d
```

### Deployed Containers:
| Service | Image / Build | Internal Port | Description |
| :--- | :--- | :--- | :--- |
| **`proxy`** | `nginx:alpine` | `80:80` | Reverse proxy routing `/api/` to backend and `/*` to frontend with Gzip compression |
| **`frontend`** | `frontend/Dockerfile` | `80` (internal) | Production-bundled static Plain CSS SPA served via Nginx Alpine |
| **`backend`** | `backend.Dockerfile` | `8000` (internal) | FastAPI service with automatic database migrations and data ingestion on boot |
| **`db`** | `postgres:16-alpine` | `5432` (internal) | PostgreSQL 16 database with persistent named volume `pgdata` and healthcheck |

### Verification & Logs
```bash
# Check running containers
docker compose ps

# View backend logs
docker compose logs -f backend

# Stop the stack
docker compose down
```

---

## 4. How to Use the Application

### 1. Catalog Browsing & Multi-Parameter Filtering (`/`)
- **Search Bar**: Type any planet, star, or system name (e.g. `TRAPPIST`, `Kepler-186`, `Proxima`).
- **View Toggle**: Switch between high-density **Grid Cards** and scientific **Tabular View** (with clickable column sorting for Radius, Mass, Period, and Temperature).
- **Categorical Presets**: One-click filters for *Habitable Zone*, *Terrestrial*, *Super-Earth*, *Gas Giant*, *Transit*, and *Radial Velocity*.
- **Range Sliders**: Filter by physical bounds (Radius, Mass, Orbital Period, Temperature, and Distance in parsecs).

### 2. Planetary Dossier & Interactive 2D Orbit Viewer (`#planet/:name`)
- Click on any planet (e.g. **TRAPPIST-1 e** or **Kepler-452 b**).
- **Physical & Ephemeris Telemetry**: Inspect measured radius ($R_\oplus$), mass ($M_\oplus$), bulk density ($\text{g/cm}^3$), semi-major axis ($a$), eccentricity ($e$), and equilibrium temperature ($T_{\text{eq}}$).
- **Interactive Orbit Viewer**:
  - **Scroll Wheel**: Zoom in and out ($0.2\times$ to $8.0\times$) smoothly.
  - **Click & Drag**: Pan across the orbital plane.
  - **Controls**: Use `[ - ]`, `[ + ]`, `[ RESET ]`, or the **`[ EXPAND ]`** toggle to resize the diagram canvas.
  - **Habitable Zone**: Visualizes the conservative Kopparapu habitable zone annulus around the host star.
- **Physical Radius Scale Diagram**: Visual comparison against Earth ($1.0 R_\oplus$) and Jupiter ($11.2 R_\oplus$).

### 3. Gemini + Model Context Protocol (MCP) AI Dossier & Q&A
- **AI Scientific Dossier**: Generates an authoritative narrative overview synthesizing classification, host star, orbital dynamics, thermal regime, and discovery facility.
- **Factual Archival Q&A**:
  - Click sample prompt pills (*"What is the mass?"*, *"Is it in the habitable zone?"*, *"How was it discovered?"*) or type custom questions.
  - Gemini executes read-only **MCP database tools** (`tool_get_planet`, `tool_get_star`, `tool_get_system`) to retrieve verified records.
  - **Zero Hallucinations**: If a parameter is unmeasured in NASA archives, the response explicitly indicates that it is unrecorded.
  - Inspect the **`MCP TOOLS`** badges and referenced fields on each answer card.

### 4. Multi-Planet System Architecture (`#system/:name`)
- View the entire family of sibling planets orbiting the same host star laid out in orbital sequence.
- Inspect stellar spectral type, effective temperature, stellar mass/radius, metallicity $[ \text{Fe/H} ]$, and multi-band apparent magnitudes ($V, B, J, H, K, \text{Gaia}, \text{TESS}$).

### 5. Side-by-Side Comparison Matrix (`#compare`)
- Click **`+ ADD TO COMPARE`** on up to 4 planets across the catalog.
- Compare physical scale, orbital parameters, and thermal properties side-by-side.

---

## 5. Running the Automated Test Suite

Run the full suite of **50 automated unit, integration, migration, and MCP tests**:
```powershell
python -m unittest discover -s tests -v
```
- **100% Passing** across data cleaning, bounds validation, ORM relationships, CSV ingestion, Alembic migrations, REST endpoints, MCP server tools, and Gemini AI services.

---

# PART 2: CONCISE PROJECT OVERVIEW

---

## 1. System Architecture & Request Lifecycle

```
NASA Exoplanet Archive (TAP API)
       │ HTTP GET (ADQL over Table: `pscomppars`)
       ▼
 Stage 1: Data Acquisition & Processing Pipeline (`run_pipeline.py`)
       │ Validates physical bounds, calculates Density, Morphology, Habitable Zone
       ▼
 Cleaned Scientific Dataset (`data/processed/exoplanets_processed.csv` - 6,354 records)
       │ Batch transaction loader (`load_database.py`)
       ▼
 Stage 2: PostgreSQL Relational Database (Alembic Migrations: `001_initial_schema.py`)
 ├── systems (coordinates, distance, multiplicity, multi-band photometry)
 ├── stars (spectral type, Teff, mass, radius, metallicity, catalog IDs)
 ├── planets (orbital dynamics, dimensions, transit flags, habitability)
 └── discoveries (method, year, facility, instrument, citation)
       │
       ▼
 Stage 3A: FastAPI REST API & Model Context Protocol (MCP) Service
 ├── REST Routes: `/api/v1/planets`, `/api/v1/systems`, `/api/v1/stars`, `/api/v1/stats`
 ├── MCP Server (`src/mcp/server.py`): `get_planet`, `get_system`, `get_star`, `search_planets`, `compare_planets`
 └── Gemini AI Service (`src/services/ai_service.py`): Grounded narrative synthesis & Q&A via MCP tools
       │ HTTP JSON / API Gateway (Nginx)
       ▼
 Stage 3B: Minimal React 18 + Plain CSS Scientific Terminal (`frontend/src/`)
 ├── Searchable Catalog & Dense Tabular Grid
 ├── Telemetry Dossier & Scalable/Scrollable 2D SVG Orbit Viewer
 ├── Multi-Planet System Architecture & Comparison Matrix
 └── Grounded Archival Q&A Panel
```

---

## 2. Layer Responsibilities Summary

| Layer | Primary Tech | File Location | Responsibility |
| :--- | :--- | :--- | :--- |
| **Data Pipeline (Stage 1)** | Pandas, Requests, ADQL | [`src/pipeline.py`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/pipeline.py), [`src/processing.py`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/processing.py), [`src/schema.py`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/schema.py) | Connects to NASA TAP API, cleans missing values, enforces physical bounds, calculates bulk density, Kopparapu habitable zone boundaries, and morphology classification. |
| **Relational DB (Stage 2)** | PostgreSQL, SQLite, SQLAlchemy 2.0, Alembic | [`src/models/`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/models/), [`alembic/`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/alembic/), [`src/services/ingestion.py`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/services/ingestion.py) | 3NF normalized schema (`systems`, `stars`, `planets`, `discoveries`), foreign-key cascades, compound B-tree indexing, and idempotent bulk ingestion. |
| **REST API (Stage 3A)** | FastAPI, Pydantic v2, Uvicorn | [`src/api/v1/`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/api/v1/), [`src/services/`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/services/) | Exposes high-performance paginated REST endpoints with dynamic multi-parameter filtering, eager joined loads, and OpenAPI documentation. |
| **MCP Server (AI Bridge)** | Python MCP SDK (`mcp.server`) | [`src/mcp/server.py`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/mcp/server.py) | Exposes controlled, read-only tools to query exoplanets, systems, and stars. Prevents the LLM from receiving raw database credentials or arbitrary SQL execution. |
| **AI Service Layer** | `google-genai` (Gemini 2.5 Flash) | [`src/services/ai_service.py`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/src/services/ai_service.py) | Executes tool calling against MCP tools; synthesizes factual summaries and answers strictly grounded on database records with offline fallback. |
| **User Interface (Stage 3B)** | React 18, TypeScript 5, Vite 6, Plain CSS | [`frontend/src/`](file:///c:/Comp/Python/SpaceProjects/ExoPlanet/frontend/src/) | Minimal, high-contrast scientific terminal UI with native hash routing, math-driven SVG schematics, and zero external CSS framework bloat. |

---

## 3. Key Astrophysics Formulas in the Codebase

1. **Mean Bulk Planetary Density**:
   $$\rho = 5.515 \cdot \frac{M / M_\oplus}{(R / R_\oplus)^3}\text{ }\left[\text{g/cm}^3\right]$$
2. **Main-Sequence Stellar Luminosity**:
   $$L_* \approx \left(\frac{M_*}{M_\odot}\right)^{3.5}\text{ }\left[L_\odot\right]$$
3. **Kopparapu Habitable Zone Boundaries**:
   $$r_{\text{inner}} = \sqrt{\frac{L_*}{1.1}}\text{ [AU]}, \quad r_{\text{outer}} = \sqrt{\frac{L_*}{0.53}}\text{ [AU]}$$
4. **Orbital Ellipse Geometry (Rendered in `OrbitDiagram.tsx`)**:
   $$\text{Semi-minor axis: } b = a\sqrt{1 - e^2}, \quad \text{Focal Offset: } c = a \cdot e$$

---

## 4. Key Engineering Commands Summary

```powershell
# Ingest data into Database
python load_database.py

# Run all 50 Tests
python -m unittest discover -s tests -v

# Start Backend Server (http://127.0.0.1:8000)
python run_server.py

# Start Frontend App (http://localhost:3000)
cd frontend; npm run dev

# Deploy full Docker Stack (http://localhost:80)
docker compose up --build -d
```

