# Exoplanet Atlas: Complete Data Platform & Scientific Research Terminal

A modern, high-performance web platform and scientific research terminal backed by **NASA Exoplanet Archive TAP API**, **PostgreSQL**, **SQLAlchemy ORM**, **Alembic Migrations**, **FastAPI REST API**, and a minimal **React 18 + TypeScript + Vite + Plain CSS** frontend with a database-grounded **AI summary and Q&A layer**.

---

## 1. System Architecture

```
NASA Exoplanet Archive (TAP API)
       │
       ▼
 Stage 1: Data Acquisition & Processing Pipeline (`run_pipeline.py`)
       │
       ▼
 Cleaned Dataset (`data/processed/exoplanets_processed.csv` - 6,354 records)
       │
       ▼
 Stage 2: Database Ingestion Service (`load_database.py`)
       │
       ▼
 PostgreSQL Relational Database (Alembic Migrations)
 ├── systems (coordinates, distance, multiplicity, multi-band photometry)
 ├── stars (spectral type, Teff, mass, radius, metallicity, catalog IDs)
 ├── planets (orbital dynamics, dimensions, transit flags, habitability)
 └── discoveries (method, year, facility, instrument, citation)
       │
       ▼
 FastAPI REST API Service (`run_server.py`)
 ├── /api/v1/planets (search, filter, sort, paginate, detail)
 ├── /api/v1/systems (search, filter, architecture, detail)
 ├── /api/v1/stars (spectral type, Teff, mass, planets)
 ├── /api/v1/stats (aggregate metrics & distributions)
 ├── /api/v1/ai (grounded natural-language summaries & factual Q&A)
 └── /docs & /redoc (Interactive Swagger / OpenAPI UI)
       │
       ▼
 Stage 3: React + TypeScript Web Application & Docker Deployment
 ├── Searchable Catalog & Filter Terminal (Grid & Table views)
 ├── Planetary Dossier Inspector (2D Orbit schematic & size scale)
 ├── Planetary System Architecture Viewer (Multi-planet family)
 ├── Side-by-Side Planet Comparison Matrix (2 to 4 worlds)
 ├── AI Scientific Narrative Dossier & Grounded Q&A Terminal
 └── Docker Compose + Nginx Multi-Service Stack (Production VPS Ready)
```

---

## 2. Visual & Scientific Design Language

The web interface is styled as a minimal, serious astronomical research terminal:
- **Palette**: Deep void black (`#050505`), dark cards (`#121212`), crisp 1px borders (`#262626`), high-contrast white text (`#ffffff`), and subtle gray telemetry indicators.
- **Styling Architecture**: Pure Plain CSS with custom variables in `frontend/src/index.css` (zero external CSS frameworks).
- **Visualizations**: Geometric 2D orbital geometry diagrams (habitable zone boundaries, host star focus, eccentric orbit lines) and relative radius scale comparisons ($R_\oplus$ and $R_{\text{Jup}}$ baselines).
- **Grounded AI**: Natural-language summaries and strict factual Q&A derived solely from database properties.

---

## 3. Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Ingestion & REST API Server
```powershell
# (Optional) Run Stage 1 Pipeline if refreshing from NASA
python run_pipeline.py

# Ingest 6,354 planets into the database
python load_database.py

# Launch FastAPI REST API server
python run_server.py
```
*API will run at `http://127.0.0.1:8000` with Swagger Docs at `http://127.0.0.1:8000/docs`.*

### 2. Frontend Web Terminal
```powershell
cd frontend
npm install
npm run dev
```
*Web interface will run at `http://localhost:3000` (automatically proxies `/api` requests to FastAPI).*

---

## 4. Production Deployment with Docker Compose

Deploy the entire stack (PostgreSQL + FastAPI Backend + Vite React Frontend + Nginx Gateway) with a single command on any Linux Server / VPS:

```bash
docker compose up --build -d
```

### Services Deployed:
- **`proxy`**: Nginx reverse proxy exposed on port `80`, routing `/api/` to backend and `/` to frontend with Gzip compression and client-side SPA fallback.
- **`frontend`**: Production-optimized static React bundle served by Nginx Alpine.
- **`backend`**: FastAPI Python 3.12 service with automatic database migrations and data loading.
- **`db`**: PostgreSQL 16 Alpine container with persistent named volume `pgdata` and automated healthchecks.

---

## 5. Automated Test Suite

Run the complete backend test suite:
```powershell
python -m unittest discover -s tests -v
```
*Tests cover Stage 1 data processing, TAP querying, SQLAlchemy models, cascade deletions, CSV ingestion and deduplication, REST API endpoints, Model Context Protocol (MCP) server tools, Gemini AI summaries/grounded Q&A, and Alembic migration upgrade/downgrades (50 tests passing 100%).*

Run the frontend TypeScript compilation and build verification:
```powershell
cd frontend
npm run build
```
*(100% type-checked with zero warnings, compiled in ~580ms).*