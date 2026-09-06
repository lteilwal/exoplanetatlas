# Python 3.12 Slim base image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for PostgreSQL compilation if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements or install dependencies
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "sqlalchemy>=2.0.0" \
    "alembic>=1.13.0" \
    "psycopg2-binary>=2.9.9" \
    "pydantic>=2.7.0" \
    "pydantic-settings>=2.2.0" \
    "python-dotenv>=1.0.0" \
    "pandas>=2.2.0" \
    "requests>=2.31.0" \
    "httpx>=0.27.0" \
    "mcp>=2.1.0" \
    "google-genai>=2.0.0"

# Copy source code and data
COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src
COPY data ./data
COPY load_database.py .
COPY run_server.py .

EXPOSE 8000

# Entrypoint script that runs migration and starts server
CMD ["python", "run_server.py", "--host", "0.0.0.0", "--port", "8000"]

