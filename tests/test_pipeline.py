"""Unit tests for src/pipeline.py."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from src.pipeline import run_pipeline


class TestPipeline(unittest.TestCase):
    """Test full pipeline orchestration and file persistence."""

    @patch("src.pipeline.fetch_raw_data")
    def test_run_pipeline_mocked(self, mock_fetch):
        """Test full pipeline run with mocked raw data."""
        mock_fetch.return_value = pd.DataFrame([
            {
                "pl_name": "Proxima Centauri b",
                "hostname": "Proxima Centauri",
                "pl_letter": "b",
                "pl_orbper": "11.186",
                "pl_orbsmax": "0.0485",
                "pl_rade": "1.07",
                "pl_bmasse": "1.17",
                "pl_insol": "0.65",
                "pl_eqt": "234.0",
                "st_teff": "3050.0",
                "st_mass": "0.12",
                "sy_dist": "1.30",
                "discoverymethod": "Radial Velocity",
                "disc_year": "2016",
            },
            {
                "pl_name": "LHS 1140 b",
                "hostname": "LHS 1140",
                "pl_letter": "b",
                "pl_orbper": "24.737",
                "pl_orbsmax": "0.0936",
                "pl_rade": "1.73",
                "pl_bmasse": "5.60",
                "pl_insol": "0.43",
                "pl_eqt": "226.0",
                "st_teff": "3216.0",
                "st_mass": "0.19",
                "sy_dist": "15.0",
                "discoverymethod": "Transit",
                "disc_year": "2017",
            },
        ])

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            raw_csv = tmp_path / "raw.csv"
            proc_csv = tmp_path / "proc.csv"
            meta_json = tmp_path / "meta.json"

            result = run_pipeline(
                curated_only=True,
                raw_csv_path=raw_csv,
                processed_csv_path=proc_csv,
                metadata_json_path=meta_json,
            )

            self.assertEqual(result["status"], "SUCCESS")
            self.assertEqual(result["output_rows"], 2)
            self.assertTrue(proc_csv.exists())
            self.assertTrue(meta_json.exists())

            # Verify saved CSV structure
            saved_df = pd.read_csv(proc_csv)
            self.assertEqual(len(saved_df), 2)
            self.assertIn("pl_name", saved_df.columns)
            self.assertIn("planet_class", saved_df.columns)
            self.assertIn("habitability_zone_est", saved_df.columns)


if __name__ == "__main__":
    unittest.main()

