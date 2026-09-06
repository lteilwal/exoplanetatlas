"""
Planet ORM model representing confirmed exoplanets.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.system import System
    from src.models.star import Star
    from src.models.discovery import Discovery


class Planet(Base):
    """
    Exoplanet entity.
    Represents a confirmed planet, its orbital parameters, physical properties,
    and observational signatures.
    """
    __tablename__ = "planets"

    # Foreign Keys
    system_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("systems.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    star_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("stars.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    # Identifiers
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    planet_letter: Mapped[str | None] = mapped_column(String(10), nullable=True, doc="Letter suffix (b, c, d...)")
    is_controversial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Orbital Dynamics
    orbital_period_days: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Orbital period (days)")
    semi_major_axis_au: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Semi-major axis (AU)")
    eccentricity: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Orbital eccentricity")
    inclination_deg: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Inclination (deg)")
    longitude_periastron_deg: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Argument of periastron (deg)")
    periastron_passage_days: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Time of periastron (days/BJD)")

    # Physical Dimensions & Mass
    radius_earth: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Radius (R_Earth)")
    radius_jupiter: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Radius (R_Jupiter)")
    mass_earth: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Mass (M_Earth)")
    mass_jupiter: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Mass (M_Jupiter)")
    best_mass_earth: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Best mass estimate (M_Earth)")
    best_mass_jupiter: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Best mass estimate (M_Jupiter)")
    mass_provenance: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="Mass provenance ('Mass', 'Msini')")
    msini_earth: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Minimum mass (M*sin(i)) in Earth masses")
    msini_jupiter: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Minimum mass (M*sin(i)) in Jupiter masses")
    density_g_cm3: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Mean bulk density (g/cm³)")

    # Thermodynamics & Insolation
    equilibrium_temp_k: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Equilibrium Temp (K)")
    insolation_earth: Mapped[float | None] = mapped_column(Float, index=True, nullable=True, doc="Insolation Flux (F_Earth)")

    # Transit & Radial Velocity Observables
    transit_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Transit duration (hours)")
    transit_depth_percent: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Transit depth (%)")
    transit_midpoint_days: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Mid-transit epoch (BJD)")
    impact_parameter: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Impact parameter b")
    ratio_planet_to_star_radius: Mapped[float | None] = mapped_column(Float, nullable=True, doc="Rp / R_star")
    radial_velocity_amplitude_m_s: Mapped[float | None] = mapped_column(Float, nullable=True, doc="RV semi-amplitude K (m/s)")

    # Derived Classifications
    planet_class: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
        nullable=True,
        doc="Morphological class (Terrestrial, Super-Earth, Sub-Neptune, Neptune-like, Gas Giant)",
    )
    habitability_zone_est: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
        nullable=True,
        doc="Insolation regime (Conservative HZ, Optimistic HZ, Hot Zone, Cold Zone)",
    )

    # Detection Flags
    tran_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    rv_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    ttv_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ptv_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ast_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    micro_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    ima_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)

    # Relationships
    system: Mapped[System] = relationship("System", back_populates="planets")
    star: Mapped[Star | None] = relationship("Star", back_populates="planets")
    discovery: Mapped[Discovery | None] = relationship(
        "Discovery",
        back_populates="planet",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Planet id={self.id} name='{self.name}' class='{self.planet_class}' period={self.orbital_period_days}d>"

