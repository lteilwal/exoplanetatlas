"""Initial schema: systems, stars, planets, discoveries

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Systems table
    op.create_table(
        'systems',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('ra', sa.Float(), nullable=True),
        sa.Column('dec', sa.Float(), nullable=True),
        sa.Column('distance_pc', sa.Float(), nullable=True),
        sa.Column('parallax_mas', sa.Float(), nullable=True),
        sa.Column('proper_motion_mas_yr', sa.Float(), nullable=True),
        sa.Column('proper_motion_ra', sa.Float(), nullable=True),
        sa.Column('proper_motion_dec', sa.Float(), nullable=True),
        sa.Column('star_count', sa.Integer(), nullable=True),
        sa.Column('planet_count', sa.Integer(), nullable=True),
        sa.Column('moon_count', sa.Integer(), nullable=True),
        sa.Column('is_circumbinary', sa.Boolean(), nullable=True),
        sa.Column('v_mag', sa.Float(), nullable=True),
        sa.Column('b_mag', sa.Float(), nullable=True),
        sa.Column('j_mag', sa.Float(), nullable=True),
        sa.Column('h_mag', sa.Float(), nullable=True),
        sa.Column('k_mag', sa.Float(), nullable=True),
        sa.Column('gaia_mag', sa.Float(), nullable=True),
        sa.Column('tess_mag', sa.Float(), nullable=True),
        sa.Column('kepler_mag', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_systems_id'), 'systems', ['id'], unique=False)
    op.create_index(op.f('ix_systems_name'), 'systems', ['name'], unique=True)
    op.create_index(op.f('ix_systems_distance_pc'), 'systems', ['distance_pc'], unique=False)
    op.create_index(op.f('ix_systems_ra'), 'systems', ['ra'], unique=False)
    op.create_index(op.f('ix_systems_dec'), 'systems', ['dec'], unique=False)
    op.create_index(op.f('ix_systems_planet_count'), 'systems', ['planet_count'], unique=False)
    op.create_index(op.f('ix_systems_is_circumbinary'), 'systems', ['is_circumbinary'], unique=False)

    # 2. Stars table
    op.create_table(
        'stars',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('hd_id', sa.String(length=50), nullable=True),
        sa.Column('hip_id', sa.String(length=50), nullable=True),
        sa.Column('tic_id', sa.String(length=50), nullable=True),
        sa.Column('gaia_dr2_id', sa.String(length=50), nullable=True),
        sa.Column('gaia_dr3_id', sa.String(length=50), nullable=True),
        sa.Column('spectral_type', sa.String(length=50), nullable=True),
        sa.Column('effective_temp_k', sa.Float(), nullable=True),
        sa.Column('radius_solar', sa.Float(), nullable=True),
        sa.Column('mass_solar', sa.Float(), nullable=True),
        sa.Column('metallicity_dex', sa.Float(), nullable=True),
        sa.Column('surface_gravity_logg', sa.Float(), nullable=True),
        sa.Column('luminosity_log_solar', sa.Float(), nullable=True),
        sa.Column('age_gyr', sa.Float(), nullable=True),
        sa.Column('density_g_cm3', sa.Float(), nullable=True),
        sa.Column('rotation_period_days', sa.Float(), nullable=True),
        sa.Column('v_sin_i_km_s', sa.Float(), nullable=True),
        sa.Column('radial_velocity_km_s', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_stars_id'), 'stars', ['id'], unique=False)
    op.create_index(op.f('ix_stars_system_id'), 'stars', ['system_id'], unique=False)
    op.create_index(op.f('ix_stars_name'), 'stars', ['name'], unique=True)
    op.create_index(op.f('ix_stars_spectral_type'), 'stars', ['spectral_type'], unique=False)
    op.create_index(op.f('ix_stars_effective_temp_k'), 'stars', ['effective_temp_k'], unique=False)
    op.create_index(op.f('ix_stars_mass_solar'), 'stars', ['mass_solar'], unique=False)

    # 3. Planets table
    op.create_table(
        'planets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('star_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('planet_letter', sa.String(length=10), nullable=True),
        sa.Column('is_controversial', sa.Boolean(), nullable=False),
        sa.Column('orbital_period_days', sa.Float(), nullable=True),
        sa.Column('semi_major_axis_au', sa.Float(), nullable=True),
        sa.Column('eccentricity', sa.Float(), nullable=True),
        sa.Column('inclination_deg', sa.Float(), nullable=True),
        sa.Column('longitude_periastron_deg', sa.Float(), nullable=True),
        sa.Column('periastron_passage_days', sa.Float(), nullable=True),
        sa.Column('radius_earth', sa.Float(), nullable=True),
        sa.Column('radius_jupiter', sa.Float(), nullable=True),
        sa.Column('mass_earth', sa.Float(), nullable=True),
        sa.Column('mass_jupiter', sa.Float(), nullable=True),
        sa.Column('best_mass_earth', sa.Float(), nullable=True),
        sa.Column('best_mass_jupiter', sa.Float(), nullable=True),
        sa.Column('mass_provenance', sa.String(length=50), nullable=True),
        sa.Column('msini_earth', sa.Float(), nullable=True),
        sa.Column('msini_jupiter', sa.Float(), nullable=True),
        sa.Column('density_g_cm3', sa.Float(), nullable=True),
        sa.Column('equilibrium_temp_k', sa.Float(), nullable=True),
        sa.Column('insolation_earth', sa.Float(), nullable=True),
        sa.Column('transit_duration_hours', sa.Float(), nullable=True),
        sa.Column('transit_depth_percent', sa.Float(), nullable=True),
        sa.Column('transit_midpoint_days', sa.Float(), nullable=True),
        sa.Column('impact_parameter', sa.Float(), nullable=True),
        sa.Column('ratio_planet_to_star_radius', sa.Float(), nullable=True),
        sa.Column('radial_velocity_amplitude_m_s', sa.Float(), nullable=True),
        sa.Column('planet_class', sa.String(length=50), nullable=True),
        sa.Column('habitability_zone_est', sa.String(length=50), nullable=True),
        sa.Column('tran_flag', sa.Boolean(), nullable=False),
        sa.Column('rv_flag', sa.Boolean(), nullable=False),
        sa.Column('ttv_flag', sa.Boolean(), nullable=False),
        sa.Column('ptv_flag', sa.Boolean(), nullable=False),
        sa.Column('ast_flag', sa.Boolean(), nullable=False),
        sa.Column('micro_flag', sa.Boolean(), nullable=False),
        sa.Column('ima_flag', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['star_id'], ['stars.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['system_id'], ['systems.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_planets_id'), 'planets', ['id'], unique=False)
    op.create_index(op.f('ix_planets_system_id'), 'planets', ['system_id'], unique=False)
    op.create_index(op.f('ix_planets_star_id'), 'planets', ['star_id'], unique=False)
    op.create_index(op.f('ix_planets_name'), 'planets', ['name'], unique=True)
    op.create_index(op.f('ix_planets_planet_class'), 'planets', ['planet_class'], unique=False)
    op.create_index(op.f('ix_planets_habitability_zone_est'), 'planets', ['habitability_zone_est'], unique=False)
    op.create_index(op.f('ix_planets_orbital_period_days'), 'planets', ['orbital_period_days'], unique=False)
    op.create_index(op.f('ix_planets_semi_major_axis_au'), 'planets', ['semi_major_axis_au'], unique=False)
    op.create_index(op.f('ix_planets_radius_earth'), 'planets', ['radius_earth'], unique=False)
    op.create_index(op.f('ix_planets_mass_earth'), 'planets', ['mass_earth'], unique=False)
    op.create_index(op.f('ix_planets_equilibrium_temp_k'), 'planets', ['equilibrium_temp_k'], unique=False)
    op.create_index(op.f('ix_planets_insolation_earth'), 'planets', ['insolation_earth'], unique=False)
    op.create_index(op.f('ix_planets_tran_flag'), 'planets', ['tran_flag'], unique=False)
    op.create_index(op.f('ix_planets_rv_flag'), 'planets', ['rv_flag'], unique=False)
    op.create_index(op.f('ix_planets_micro_flag'), 'planets', ['micro_flag'], unique=False)
    op.create_index(op.f('ix_planets_ima_flag'), 'planets', ['ima_flag'], unique=False)

    # 4. Discoveries table
    op.create_table(
        'discoveries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('planet_id', sa.Integer(), nullable=False),
        sa.Column('discovery_method', sa.String(length=100), nullable=False),
        sa.Column('discovery_year', sa.Integer(), nullable=True),
        sa.Column('discovery_facility', sa.String(length=200), nullable=True),
        sa.Column('discovery_instrument', sa.String(length=200), nullable=True),
        sa.Column('discovery_locale', sa.String(length=50), nullable=True),
        sa.Column('publication_date', sa.String(length=20), nullable=True),
        sa.Column('reference_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['planet_id'], ['planets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('planet_id')
    )
    op.create_index(op.f('ix_discoveries_id'), 'discoveries', ['id'], unique=False)
    op.create_index(op.f('ix_discoveries_planet_id'), 'discoveries', ['planet_id'], unique=True)
    op.create_index(op.f('ix_discoveries_discovery_method'), 'discoveries', ['discovery_method'], unique=False)
    op.create_index(op.f('ix_discoveries_discovery_year'), 'discoveries', ['discovery_year'], unique=False)
    op.create_index(op.f('ix_discoveries_discovery_facility'), 'discoveries', ['discovery_facility'], unique=False)


def downgrade() -> None:
    op.drop_table('discoveries')
    op.drop_table('planets')
    op.drop_table('stars')
    op.drop_table('systems')

