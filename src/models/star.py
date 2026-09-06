"""
Star ORM model representing host stars.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.system import System
    from src.models.planet import Planet


class Star(Base):
    """
    Host Star entity.
    Represents an individual star belonging to a planetary system.
    """
    __tablename__ = "stars"

    # System Foreign Key
    system_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("systems.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Identifiers
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hd_id: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="Henry Draper ID")
    hip_id: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="Hipparcos ID")
    tic_id: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="TESS Input Catalog ID")
    gaia_dr2_id: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="Gaia DR2 Source ID")
    gaia_dr3_id: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="Gaia DR3 Source ID")

    # Astrophysical Properties
    spectral_type: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True, doc="Spectral Type (e.g. G2V)")
    effective_temp_k: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Effective Temperature (K)")
    radius_solar: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Radius (R_Sun)")
    mass_solar: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Mass (M_Sun)")
    metallicity_dex: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Metallicity [Fe/H] (dex)")
    surface_gravity_logg: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Surface gravity log(g) (cgs)")
    luminosity_log_solar: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Luminosity log10(L_Sun)")
    age_gyr: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Stellar age (Gyr)")
    density_g_cm3: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Mean stellar density (g/cm³)")

    # Kinematics & Rotation
    rotation_period_days: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Rotation period (days)")
    v_sin_i_km_s: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Rotational velocity v*sin(i) (km/s)")
    radial_velocity_km_s: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Radial velocity (km/s)")

    # Relationships
    system: Mapped[System] = relationship("System", back_populates="stars")
    planets: Mapped[List[Planet]] = relationship(
        "Planet",
        back_populates="star",
        order_by="Planet.name",
    )

    def __repr__(self) -> str:
        return f"<Star id={self.id} name='{self.name}' spec='{self.spectral_type}' teff={self.effective_temp_k}K>"

