"""Unit tests for Systems, Stars, and Stats API endpoints."""
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.deps import get_db
from src.db.base import Base
from src.main import app
from src.models import Discovery, Planet, Star, System


class TestApiSystemsAndStats(unittest.TestCase):
    """Test /api/v1/systems, /api/v1/stars, /api/v1/stats, and root/health endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.TestingSession = sessionmaker(bind=cls.engine)
        cls.client = TestClient(app)

        db = cls.TestingSession()
        sys = System(name="Kepler-11", distance_pc=646.0, planet_count=6, is_circumbinary=False)
        db.add(sys)
        db.flush()

        star = Star(system_id=sys.id, name="Kepler-11", spectral_type="G2V", effective_temp_k=5680.0)
        db.add(star)
        db.flush()

        p = Planet(
            system_id=sys.id,
            star_id=star.id,
            name="Kepler-11 b",
            radius_earth=1.83,
            mass_earth=2.78,
            planet_class="Super-Earth",
            habitability_zone_est="Hot Zone",
        )
        db.add(p)
        db.flush()

        d = Discovery(planet_id=p.id, discovery_method="Transit", discovery_year=2011)
        db.add(d)
        db.commit()
        db.close()

    def setUp(self):
        def override_get_db():
            db = self.TestingSession()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_root_and_health(self):
        """Test root / and /health endpoints."""
        r_root = self.client.get("/")
        self.assertEqual(r_root.status_code, 200)
        self.assertEqual(r_root.json()["status"], "ONLINE")

        r_health = self.client.get("/health")
        self.assertEqual(r_health.status_code, 200)
        self.assertEqual(r_health.json()["status"], "HEALTHY")

    def test_list_systems(self):
        """Test GET /api/v1/systems."""
        response = self.client.get("/api/v1/systems")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["name"], "Kepler-11")

    def test_get_system_detail(self):
        """Test GET /api/v1/systems/{name} with nested planets and stars."""
        response = self.client.get("/api/v1/systems/Kepler-11")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Kepler-11")
        self.assertEqual(len(data["stars"]), 1)
        self.assertEqual(len(data["planets"]), 1)
        self.assertEqual(data["planets"][0]["name"], "Kepler-11 b")

    def test_list_stars(self):
        """Test GET /api/v1/stars."""
        response = self.client.get("/api/v1/stars")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["spectral_type"], "G2V")

    def test_get_stats(self):
        """Test GET /api/v1/stats."""
        response = self.client.get("/api/v1/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_planets"], 1)
        self.assertEqual(data["total_systems"], 1)
        self.assertEqual(data["total_stars"], 1)
        self.assertIn("Super-Earth", data["planet_class_distribution"])
        self.assertIn("Transit", data["discovery_method_distribution"])


if __name__ == "__main__":
    unittest.main()

