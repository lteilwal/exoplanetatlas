"""
Unit tests for Exoplanet Atlas Model Context Protocol (MCP) Server and Tools.
"""
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.models import Discovery, Planet, Star, System
from src.mcp.server import (
    tool_compare_planets,
    tool_get_planet,
    tool_get_star,
    tool_get_system,
    tool_search_planets,
)
import src.db.session as session_module


class TestMCPServer(unittest.TestCase):
    """Test MCP tool execution against database."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        # Patch SessionLocal in session module for MCP tools
        cls.orig_session_local = session_module.SessionLocal
        session_module.SessionLocal = cls.SessionLocal

        # Populate test fixtures
        db = cls.SessionLocal()
        sys = System(
            name="MCP-System-1",
            distance_pc=25.0,
            star_count=1,
            planet_count=2,
            ra=180.5,
            dec=-15.2,
        )
        db.add(sys)
        db.flush()

        star = Star(
            system_id=sys.id,
            name="MCP-Star-1",
            spectral_type="G2V",
            effective_temp_k=5780.0,
            mass_solar=1.02,
            radius_solar=1.0,
        )
        db.add(star)
        db.flush()

        p1 = Planet(
            system_id=sys.id,
            star_id=star.id,
            name="MCP-Planet-1 b",
            radius_earth=1.05,
            mass_earth=1.12,
            orbital_period_days=28.5,
            semi_major_axis_au=0.18,
            equilibrium_temp_k=295.0,
            planet_class="Terrestrial",
            habitability_zone_est="Conservative Habitable Zone",
        )
        p2 = Planet(
            system_id=sys.id,
            star_id=star.id,
            name="MCP-Planet-1 c",
            radius_earth=2.45,
            mass_earth=6.8,
            orbital_period_days=85.2,
            semi_major_axis_au=0.38,
            equilibrium_temp_k=210.0,
            planet_class="Sub-Neptune",
            habitability_zone_est="Cold Zone",
        )
        db.add_all([p1, p2])
        db.flush()

        disc1 = Discovery(planet_id=p1.id, discovery_method="Transit", discovery_year=2024, discovery_facility="SpaceTel")
        disc2 = Discovery(planet_id=p2.id, discovery_method="Transit", discovery_year=2024, discovery_facility="SpaceTel")
        db.add_all([disc1, disc2])
        db.commit()
        db.close()

    @classmethod
    def tearDownClass(cls):
        session_module.SessionLocal = cls.orig_session_local

    def test_tool_get_planet_found(self):
        result = tool_get_planet("MCP-Planet-1 b")
        self.assertTrue(result.get("found"))
        self.assertEqual(result.get("name"), "MCP-Planet-1 b")
        self.assertEqual(result.get("planet_class"), "Terrestrial")
        self.assertAlmostEqual(result.get("radius_earth"), 1.05)
        self.assertIsNotNone(result.get("system"))
        self.assertIsNotNone(result.get("star"))

    def test_tool_get_planet_not_found(self):
        result = tool_get_planet("NonExistentPlanet999")
        self.assertFalse(result.get("found"))
        self.assertIn("was not found", result.get("message"))

    def test_tool_get_system(self):
        result = tool_get_system("MCP-System-1")
        self.assertTrue(result.get("found"))
        self.assertEqual(result.get("name"), "MCP-System-1")
        self.assertEqual(result.get("planet_count"), 2)
        self.assertEqual(len(result.get("planets", [])), 2)

    def test_tool_get_star(self):
        result = tool_get_star("MCP-Star-1")
        self.assertTrue(result.get("found"))
        self.assertEqual(result.get("name"), "MCP-Star-1")
        self.assertEqual(result.get("spectral_type"), "G2V")
        self.assertEqual(len(result.get("planets", [])), 2)

    def test_tool_search_planets(self):
        search_res = tool_search_planets(query="MCP-Planet", limit=10)
        self.assertEqual(search_res.get("returned_count"), 2)
        self.assertEqual(search_res.get("total_matches"), 2)

    def test_tool_search_planets_with_class_filter(self):
        search_res = tool_search_planets(planet_class="Terrestrial", limit=10)
        self.assertEqual(search_res.get("returned_count"), 1)
        self.assertEqual(search_res.get("planets")[0]["name"], "MCP-Planet-1 b")

    def test_tool_compare_planets(self):
        comp_res = tool_compare_planets(["MCP-Planet-1 b", "MCP-Planet-1 c"])
        self.assertEqual(comp_res.get("comparison_count"), 2)
        planets = comp_res.get("planets", [])
        self.assertEqual(planets[0]["name"], "MCP-Planet-1 b")
        self.assertEqual(planets[1]["name"], "MCP-Planet-1 c")


if __name__ == "__main__":
    unittest.main()

