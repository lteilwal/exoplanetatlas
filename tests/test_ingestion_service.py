"""Unit tests for database ingestion service."""
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.models import Discovery, Planet, Star, System
from src.services.ingestion import ingest_from_csv


class TestIngestionService(unittest.TestCase):
    """Test reading CSV, deduplicating entities, and upserting into database."""

    def setUp(self):
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

    def test_ingest_from_sample_csv(self):
        """Test end-to-end CSV ingestion into relational models."""
        sample_df = pd.DataFrame([
            {
                "pl_name": "TRAPPIST-1 b",
                "hostname": "TRAPPIST-1",
                "sy_name": "TRAPPIST-1",
                "pl_letter": "b",
                "pl_orbper": 1.51,
                "pl_rade": 1.11,
                "pl_masse": 1.37,
                "st_teff": 2566.0,
                "st_mass": 0.0898,
                "sy_dist": 12.1,
                "discoverymethod": "Transit",
                "disc_year": 2016,
                "planet_class": "Terrestrial",
                "habitability_zone_est": "Hot Zone",
                "calc_density": 5.48,
            },
            {
                "pl_name": "TRAPPIST-1 c",
                "hostname": "TRAPPIST-1",
                "sy_name": "TRAPPIST-1",
                "pl_letter": "c",
                "pl_orbper": 2.42,
                "pl_rade": 1.09,
                "pl_masse": 1.30,
                "st_teff": 2566.0,
                "st_mass": 0.0898,
                "sy_dist": 12.1,
                "discoverymethod": "Transit",
                "disc_year": 2016,
                "planet_class": "Terrestrial",
                "habitability_zone_est": "Hot Zone",
                "calc_density": 5.50,
            },
            {
                "pl_name": "HD 209458 b",
                "hostname": "HD 209458",
                "sy_name": "HD 209458",
                "pl_letter": "b",
                "pl_orbper": 3.52,
                "pl_rade": 15.8,
                "pl_masse": 219.0,
                "st_teff": 6065.0,
                "st_mass": 1.15,
                "sy_dist": 48.3,
                "discoverymethod": "Transit",
                "disc_year": 1999,
                "planet_class": "Gas Giant",
                "habitability_zone_est": "Hot Zone",
                "calc_density": 0.31,
            },
        ])

        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
            sample_df.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            stats = ingest_from_csv(csv_path=temp_path, db=self.db)

            self.assertEqual(stats["rows_processed"], 3)
            # 2 distinct systems (TRAPPIST-1 and HD 209458)
            self.assertEqual(stats["systems_count"], 2)
            # 2 distinct stars
            self.assertEqual(stats["stars_count"], 2)
            # 3 planets
            self.assertEqual(stats["planets_count"], 3)
            # 3 discoveries
            self.assertEqual(stats["discoveries_count"], 3)

            # Check relationships in database
            trappist_sys = self.db.query(System).filter(System.name == "TRAPPIST-1").first()
            self.assertIsNotNone(trappist_sys)
            self.assertEqual(len(trappist_sys.planets), 2)
            self.assertEqual(len(trappist_sys.stars), 1)

            # Check planet properties
            trappist_b = self.db.query(Planet).filter(Planet.name == "TRAPPIST-1 b").first()
            self.assertIsNotNone(trappist_b)
            self.assertEqual(trappist_b.planet_class, "Terrestrial")
            self.assertEqual(trappist_b.discovery.discovery_method, "Transit")

        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

