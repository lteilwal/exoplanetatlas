"""
Discovery ORM model representing discovery circumstances and bibliography.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.planet import Planet


class Discovery(Base):
    """
    Discovery metadata entity.
    Stores how, when, and where a planet was detected.
    """
    __tablename__ = "discoveries"

    # Planet Foreign Key (1-to-1 relationship)
    planet_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("planets.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    # Discovery Details
    discovery_method: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
        doc="Detection method (e.g. Transit, Radial Velocity)",
    )
    discovery_year: Mapped[int | None] = mapped_column(
        Integer,
        index=True,
        nullable=True,
        doc="Year of confirmation publication",
    )
    discovery_facility: Mapped[str | None] = mapped_column(
        String(200),
        index=True,
        nullable=True,
        doc="Observatory / Space Telescope",
    )
    discovery_instrument: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        doc="Detecting instrument / spectrograph",
    )
    discovery_locale: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="'Space' or 'Ground'",
    )
    publication_date: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Publication date (YYYY-MM)",
    )
    reference_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Bibliographic ADS reference key",
    )

    # Relationship
    planet: Mapped[Planet] = relationship("Planet", back_populates="discovery")

    def __repr__(self) -> str:
        return f"<Discovery planet_id={self.planet_id} method='{self.discovery_method}' year={self.discovery_year}>"

