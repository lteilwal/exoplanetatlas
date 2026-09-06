"""Unit tests for SQLAlchemy ORM models."""
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.models import Discovery, Planet, Star, System


class TestModels(unittest.TestCase):
    """Test ORM models, relationships, and cascade operations."""

    def setUp(self):
        """Create in-memory SQLite database for isolated testing."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_system_star_planet_discovery_hierarchy(self):
        """Test creating a complete planetary system hierarchy."""
        # 1. Create System
        system = System(
            name="TRAPPIST-1",
            ra=346.622,
            dec=-5.041,
            distance_pc=12.1,
            star_count=1,
            planet_count=7,
        )
        self.db.add(system)
        self.db.flush()

        self.assertIsNotNone(system.id)
        self.assertEqual(system.name, "TRAPPIST-1")

        # 2. Create Star
        star = Star(
            system_id=system.id,
            name="TRAPPIST-1",
            spectral_type="M8V",
            effective_temp_k=2566.0,
            mass_solar=0.0898,
        )
        self.db.add(star)
        self.db.flush()

        self.assertIsNotNone(star.id)
        self.assertEqual(star.system_id, system.id)

        # 3. Create Planet
        planet = Planet(
            system_id=system.id,
            star_id=star.id,
            name="TRAPPIST-1 e",
            planet_letter="e",
            orbital_period_days=6.0996,
            radius_earth=0.920,
            mass_earth=0.692,
            planet_class="Terrestrial",
            habitability_zone_est="Conservative Habitable Zone",
        )
        self.db.add(planet)
        self.db.flush()

        self.assertIsNotNone(planet.id)

        # 4. Create Discovery
        discovery = Discovery(
            planet_id=planet.id,
            discovery_method="Transit",
            discovery_year=2017,
            discovery_facility="TRAPPIST",
        )
        self.db.add(discovery)
        self.db.commit()

        # Query back and verify relationships
        queried_sys = self.db.query(System).filter(System.name == "TRAPPIST-1").first()
        self.assertIsNotNone(queried_sys)
        self.assertEqual(len(queried_sys.stars), 1)
        self.assertEqual(len(queried_sys.planets), 1)
        self.assertEqual(queried_sys.planets[0].name, "TRAPPIST-1 e")
        self.assertEqual(queried_sys.planets[0].discovery.discovery_method, "Transit")
        self.assertEqual(queried_sys.planets[0].star.spectral_type, "M8V")

    def test_cascade_delete_system_removes_planets_and_stars(self):
        """Ensure deleting a system cascades to stars, planets, and discoveries."""
        system = System(name="Kepler-186", distance_pc=178.0)
        self.db.add(system)
        self.db.flush()

        star = Star(system_id=system.id, name="Kepler-186", spectral_type="M1V")
        self.db.add(star)
        self.db.flush()

        planet = Planet(system_id=system.id, star_id=star.id, name="Kepler-186 f")
        self.db.add(planet)
        self.db.flush()

        discovery = Discovery(planet_id=planet.id, discovery_method="Transit")
        self.db.add(discovery)
        self.db.commit()

        # Delete system
        self.db.delete(system)
        self.db.commit()

        self.assertEqual(self.db.query(System).count(), 0)
        self.assertEqual(self.db.query(Star).count(), 0)
        self.assertEqual(self.db.query(Planet).count(), 0)
        self.assertEqual(self.db.query(Discovery).count(), 0)


if __name__ == "__main__":
    unittest.main()

