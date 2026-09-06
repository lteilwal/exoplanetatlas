"""
Configuration module for Exoplanet Atlas backend service.

Reads settings from environment variables and `.env` files using Pydantic Settings.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root path of the repository
REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings and environment configuration."""

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "Exoplanet Atlas API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = (
        "Backend REST API service providing structured access to confirmed exoplanets, "
        "host stars, and planetary systems based on NASA Exoplanet Archive data."
    )

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    # Database settings
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_HOST: str = Field(default="127.0.0.1")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="exoplanet_db")

    # Explicit Database URL override if specified in environment
    DATABASE_URL: Optional[str] = None

    # AI / Gemini settings
    GEMINI_API_KEY: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")

    # SQLite fallback path for seamless development / test mode
    SQLITE_DB_PATH: Path = REPO_ROOT / "data" / "exoplanet.db"

    # Ingestion source files
    PROCESSED_CSV_PATH: Path = REPO_ROOT / "data" / "processed" / "exoplanets_processed.csv"
    RAW_CSV_PATH: Path = REPO_ROOT / "data" / "raw" / "exoplanets_raw.csv"

    # Pagination limits
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 100

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Compute effective database connection URI.
        Prefers explicit DATABASE_URL, otherwise constructs PostgreSQL URI.
        """
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url

        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

