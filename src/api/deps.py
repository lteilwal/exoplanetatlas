"""
FastAPI dependency injection utilities.
"""
from typing import Generator
from sqlalchemy.orm import Session
from src.db.session import get_db

__all__ = ["get_db"]

