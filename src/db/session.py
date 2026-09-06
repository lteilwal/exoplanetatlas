"""
Database session management, engine creation, and dependency injection.
"""
from __future__ import annotations

import logging
from typing import Generator

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings

logger = logging.getLogger(__name__)


def create_resilient_engine() -> Engine:
    """
    Attempt to initialize the configured database engine (e.g. PostgreSQL).
    If connection fails, gracefully fall back to SQLite for local development and testing.
    """
    configured_uri = settings.SQLALCHEMY_DATABASE_URI
    is_sqlite = configured_uri.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}

    try:
        eng = create_engine(
            configured_uri,
            pool_pre_ping=True,
            connect_args=connect_args,
            echo=settings.DEBUG,
        )
        # Test connection
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Database connection verified: {configured_uri}")
        return eng
    except Exception as exc:
        if not is_sqlite:
            logger.warning(
                f"Could not establish connection to PostgreSQL ({configured_uri}): {exc}. "
                f"Falling back to local SQLite at {settings.SQLITE_DB_PATH}. "
                f"Configure PostgreSQL credentials in .env to use PostgreSQL."
            )
            settings.SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            fallback_uri = f"sqlite:///{settings.SQLITE_DB_PATH}"
            return create_engine(
                fallback_uri,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
            )
        raise exc


# Global engine instance
engine: Engine = create_resilient_engine()

# Backwards-compatible alias
get_engine = create_resilient_engine

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session.
    Closes the session upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(target_engine: Engine | None = None) -> None:
    """
    Create all database tables defined in the ORM metadata if they do not exist.
    """
    from src.db.base import Base
    import src.models  # Ensure all models are imported so they register with Base.metadata

    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    logger.info(f"Database tables initialized on {eng.url}.")

