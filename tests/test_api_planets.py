"""Unit tests for Planets API endpoints."""
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.deps import get_db
from src.db.base import Base
from src.main import app
from src.models import Discovery, Planet, Star, System


class TestApiPlanets(unittest.TestCase):
    """Test /api/v1/planets endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up test database and test client."""
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.TestingSession = sessionmaker(bind=cls.engine)
        cls.client = TestClient(app)

        # Populate test fixtures
        db = cls.TestingSession()
        sys1 = System(name="Proxima Centauri", distance_pc=1.3, planet_count=1)
        sys2 = System(name="TRAPPIST-1", distance_pc=12.1, planet_count=7)
        db.add_all([sys1, sys2])
        db.flush()

        star1 = Star(system_id=sys1.id, name="Proxima Centauri", spectral_type="M5.5V", effective_temp_k=3050.0)
        star2 = Star(system_id=sys2.id, name="TRAPPIST-1", spectral_type="M8V", effective_temp_k=2566.0)
        db.add_all([star1, star2])
        db.flush()

        p1 = Planet(
            system_id=sys1.id,
            star_id=star1.id,
            name="Proxima Centauri b",
            planet_letter="b",
            orbital_period_days=11.186,
            radius_earth=1.07,
            mass_earth=1.17,
            planet_class="Terrestrial",
            habitability_zone_est="Conservative Habitable Zone",
        )
        p2 = Planet(
            system_id=sys2.id,
            star_id=star2.id,
            name="TRAPPIST-1 e",
            planet_letter="e",
            orbital_period_days=6.0996,
            radius_earth=0.920,
            mass_earth=0.692,
            planet_class="Terrestrial",
            habitability_zone_est="Conservative Habitable Zone",
        )
        db.add_all([p1, p2])
        db.flush()

        d1 = Discovery(planet_id=p1.id, discovery_method="Radial Velocity", discovery_year=2016)
        d2 = Discovery(planet_id=p2.id, discovery_method="Transit", discovery_year=2017)
        db.add_all([d1, d2])
        db.commit()
        db.close()

    def setUp(self):
        """Override get_db dependency for each test."""
        def override_get_db():
            db = self.TestingSession()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_list_planets_pagination(self):
        """Test GET /api/v1/planets returns paginated structure."""
        response = self.client.get("/api/v1/planets?page=1&page_size=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["page"], 1)
        self.assertEqual(len(data["items"]), 2)

    def test_filter_planets_by_discovery_method(self):
        """Test filtering by discovery method."""
        response = self.client.get("/api/v1/planets?discovery_method=Transit")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["name"], "TRAPPIST-1 e")

    def test_search_planets(self):
        """Test substring search."""
        response = self.client.get("/api/v1/planets?search=Proxima")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["name"], "Proxima Centauri b")

    def test_get_planet_by_name(self):
        """Test GET /api/v1/planets/{name}."""
        response = self.client.get("/api/v1/planets/TRAPPIST-1%20e")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "TRAPPIST-1 e")
        self.assertEqual(data["planet_class"], "Terrestrial")
        self.assertIsNotNone(data["star"])
        self.assertIsNotNone(data["system"])
        self.assertEqual(data["discovery"]["discovery_method"], "Transit")

    def test_get_planet_not_found(self):
        """Test GET /api/v1/planets/non-existent returns 404."""
        response = self.client.get("/api/v1/planets/NonExistentPlanet999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

