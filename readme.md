# Exoplanet Atlas

A full-stack scientific data platform for exploring NASA exoplanet data.

The system acquires and processes data from the NASA Exoplanet Archive, stores it in PostgreSQL, exposes it through a FastAPI REST API, and provides a React/TypeScript research interface with searchable catalogs, planetary-system visualization, comparisons, and database-grounded AI Q&A using Gemini and MCP.

### Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · Alembic · MCP · Gemini · React · Docker · Nginx

### Architecture

NASA Exoplanet Archive → Data Pipeline → PostgreSQL → FastAPI + MCP/AI → Frontend

### Run locally

```bash
python run_pipeline.py
python load_database.py
python run_server.py

cd frontend
npm install
npm run dev
