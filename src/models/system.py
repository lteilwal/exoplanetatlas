"""
System ORM model representing planetary/stellar systems.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.star import Star
    from src.models.planet import Planet


class System(Base):
    """
    Planetary System entity.
    Represents a host system containing one or more stars and orbiting planets.
    """
    __tablename__ = "systems"

    # Primary identification
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    # Coordinates & Kinematics (ICRS J2000)
    ra: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Right Ascension (deg)")
    dec: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Declination (deg)")
    distance_pc: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Distance from Sun (pc)")
    parallax_mas: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Trigonometric parallax (mas)")
    proper_motion_mas_yr: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Total proper motion (mas/yr)")
    proper_motion_ra: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Proper motion in RA (mas/yr)")
    proper_motion_dec: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Proper motion in Dec (mas/yr)")

    # System Multiplicity & Architecture
    star_count: Mapped[int | None] = mapped_column(Integer, default=1, nullable=True, doc="Number of stars in system")
    planet_count: Mapped[int | None] = mapped_column(Integer, default=1, index=True, nullable=True, doc="Number of confirmed planets")
    moon_count: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True, doc="Number of confirmed moons")
    is_circumbinary: Mapped[bool | None] = mapped_column(Boolean, default=False, index=True, nullable=True, doc="Circumbinary flag")

    # Multi-band Photometry (apparent magnitudes)
    v_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Johnson V magnitude")
    b_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Johnson B magnitude")
    j_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="2MASS J magnitude")
    h_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="2MASS H magnitude")
    k_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="2MASS Ks magnitude")
    gaia_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Gaia G magnitude")
    tess_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="TESS magnitude")
    kepler_mag: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Kepler magnitude")

    # Relationships
    stars: Mapped[List[Star]] = relationship(
        "Star",
        back_populates="system",
        cascade="all, delete-orphan",
        order_by="Star.name",
    )
    planets: Mapped[List[Planet]] = relationship(
        "Planet",
        back_populates="system",
        cascade="all, delete-orphan",
        order_by="Planet.name",
    )

    def __repr__(self) -> str:
        return f"<System id={self.id} name='{self.name}' planets={self.planet_count} dist={self.distance_pc}pc>"

