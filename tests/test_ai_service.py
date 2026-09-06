"""
Unit and API integration tests for Gemini + MCP AI Service and Endpoints.
"""
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.main import app
from src.api.deps import get_db
from src.models import Discovery, Planet, Star, System
from src.services.ai_service import (
    ask_planet_question_ai,
    general_chat_ai,
    generate_planet_summary_ai,
)
import src.db.session as session_module


class TestAIServiceWithMCP(unittest.TestCase):
    """Test grounded AI summary and question answering via MCP tools."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        cls.orig_session_local = session_module.SessionLocal
        session_module.SessionLocal = cls.SessionLocal

        db = cls.SessionLocal()
        sys = System(name="AI-System-1", distance_pc=10.0, star_count=1, planet_count=1)
        db.add(sys)
        db.flush()

        star = Star(system_id=sys.id, name="AI-Star-1", spectral_type="G2V", effective_temp_k=5800.0)
        db.add(star)
        db.flush()

        planet = Planet(
            system_id=sys.id,
            star_id=star.id,
            name="AI-Planet-1",
            radius_earth=1.1,
            mass_earth=1.4,
            orbital_period_days=365.25,
            semi_major_axis_au=1.0,
            equilibrium_temp_k=255.0,
            planet_class="Terrestrial",
            habitability_zone_est="Conservative Habitable Zone",
        )
        db.add(planet)
        db.flush()

        disc = Discovery(planet_id=planet.id, discovery_method="Transit", discovery_year=2024, discovery_facility="SpaceLab")
        db.add(disc)
        db.commit()
        db.close()

    @classmethod
    def tearDownClass(cls):
        session_module.SessionLocal = cls.orig_session_local

    def test_summary_generation_offline(self):
        summary, key_facts, tools = generate_planet_summary_ai("AI-Planet-1")
        self.assertIn("AI-Planet-1", summary)
        self.assertIn("Terrestrial", summary)
        self.assertIn("tool_get_planet", tools)
        self.assertGreaterEqual(len(key_facts), 3)

    def test_qa_offline_mass(self):
        ans, tools, fields = ask_planet_question_ai("AI-Planet-1", "What is the mass of this planet?")
        self.assertIn("1.40 Earth masses", ans)
        self.assertIn("tool_get_planet", tools)

    def test_qa_offline_missing_planet(self):
        ans, tools, fields = ask_planet_question_ai("UnknownWorld", "What is the radius?")
        self.assertIn("not recorded in the database", ans)

    def test_chat_offline_search(self):
        res, tools = general_chat_ai("AI-Planet")
        self.assertIn("AI-Planet-1", res)
        self.assertTrue(len(tools) > 0)


class TestAIApiEndpoints(unittest.TestCase):
    """Integration tests for FastAPI AI endpoints with mocked DB session."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        cls.orig_session_local = session_module.SessionLocal
        session_module.SessionLocal = cls.SessionLocal

        db = cls.SessionLocal()
        sys = System(name="AI-System-Test", distance_pc=12.0, star_count=1, planet_count=1)
        db.add(sys)
        db.flush()

        star = Star(system_id=sys.id, name="AI-Star-Test", spectral_type="M2V", effective_temp_k=3500.0)
        db.add(star)
        db.flush()

        planet = Planet(
            system_id=sys.id,
            star_id=star.id,
            name="AI-Planet-Test",
            radius_earth=1.2,
            mass_earth=2.1,
            orbital_period_days=14.5,
            equilibrium_temp_k=280.0,
            planet_class="Super-Earth",
            habitability_zone_est="Optimistic Habitable Zone",
        )
        db.add(planet)
        db.flush()

        disc = Discovery(planet_id=planet.id, discovery_method="Transit", discovery_year=2023, discovery_facility="Kepler")
        db.add(disc)
        db.commit()
        db.close()

    @classmethod
    def tearDownClass(cls):
        session_module.SessionLocal = cls.orig_session_local

    def override_get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def setUp(self):
        app.dependency_overrides[get_db] = self.override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_get_ai_summary_endpoint(self):
        response = self.client.get("/api/v1/ai/planets/AI-Planet-Test/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["planet_name"], "AI-Planet-Test")
        self.assertIn("Super-Earth", data["summary"])
        self.assertIn("tool_get_planet", data["tools_used"])

    def test_post_ai_qa_endpoint(self):
        payload = {"question": "What is the discovery method and temperature?"}
        response = self.client.post("/api/v1/ai/planets/AI-Planet-Test/qa", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["planet_name"], "AI-Planet-Test")
        self.assertIn("280", data["answer"])

    def test_post_ai_chat_endpoint(self):
        payload = {"message": "AI-Planet-Test"}
        response = self.client.post("/api/v1/ai/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("AI-Planet-Test", data["response"])

    def test_ai_planet_not_found(self):
        response = self.client.get("/api/v1/ai/planets/NonExistent/summary")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
