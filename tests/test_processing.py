"""Unit tests for src/processing.py."""
import unittest
import numpy as np
import pandas as pd

from src.processing import (
    add_derived_astronomical_features,
    clean_dataframe,
    filter_and_validate,
    sanitize_dataframe,
    select_schema_columns,
)


class TestProcessing(unittest.TestCase):
    """Test data sanitization, physical validation, derived calculations, and schema alignment."""

    def setUp(self):
        """Create sample test dataframe."""
        self.sample_data = pd.DataFrame([
            {
                "pl_name": "  TRAPPIST-1 e  ",
                "hostname": "TRAPPIST-1",
                "pl_letter": "e",
                "pl_orbper": "6.0996",
                "pl_orbsmax": "0.02928",
                "pl_rade": "0.920",
                "pl_bmasse": "0.692",
                "pl_insol": "0.662",
                "pl_eqt": "251.0",
                "pl_orbeccen": "0.005",
                "st_teff": "2566.0",
                "st_mass": "0.0898",
                "sy_dist": "12.1",
                "discoverymethod": "Transit",
                "disc_year": "2017",
            },
            {
                "pl_name": "Kepler-22 b",
                "hostname": "Kepler-22",
                "pl_letter": "b",
                "pl_orbper": "289.86",
                "pl_orbsmax": "0.849",
                "pl_rade": "2.38",
                "pl_bmasse": np.nan,
                "pl_insol": "1.10",
                "pl_eqt": "262.0",
                "pl_orbeccen": "0.0",
                "st_teff": "5518.0",
                "st_mass": "0.97",
                "sy_dist": "194.0",
                "discoverymethod": "Transit",
                "disc_year": "2011",
            },
            {
                "pl_name": "HD 209458 b",
                "hostname": "HD 209458",
                "pl_letter": "b",
                "pl_orbper": "-3.52",  # Invalid negative period
                "pl_orbsmax": "0.047",
                "pl_rade": "15.8",     # Gas giant (1.4 R_J)
                "pl_bmasse": "219.0",  # ~0.69 M_J
                "pl_insol": "1000.0",
                "pl_eqt": "1450.0",
                "pl_orbeccen": "1.5",  # Invalid eccentricity >= 1
                "st_teff": "6065.0",
                "st_mass": "1.15",
                "sy_dist": "48.3",
                "discoverymethod": "Transit",
                "disc_year": "1999",
            },
            {
                "pl_name": "   ",      # Missing planet name
                "hostname": "Ghost Star",
                "pl_orbper": "10.0",
            }
        ])

    def test_sanitize_dataframe(self):
        """Test whitespace stripping and string null conversions."""
        sanitized, actions = sanitize_dataframe(self.sample_data)
        self.assertEqual(sanitized.iloc[0]["pl_name"], "TRAPPIST-1 e")
        self.assertGreater(len(actions), 0)

    def test_filter_and_validate(self):
        """Test removal of missing names and nullification of non-physical values."""
        sanitized, _ = sanitize_dataframe(self.sample_data)
        validated, actions = filter_and_validate(sanitized)

        # Missing name row should be dropped
        self.assertEqual(len(validated), 3)

        # Invalid negative period should be replaced with NaN
        hd_row = validated[validated["pl_name"] == "HD 209458 b"].iloc[0]
        self.assertTrue(pd.isna(hd_row["pl_orbper"]))

        # Invalid eccentricity >= 1 should be NaN
        self.assertTrue(pd.isna(hd_row["pl_orbeccen"]))

    def test_derived_astronomical_features(self):
        """Test planet classification, habitability zones, and density calculation."""
        sanitized, _ = sanitize_dataframe(self.sample_data)
        validated, _ = filter_and_validate(sanitized)
        enriched, _ = add_derived_astronomical_features(validated)

        self.assertIn("planet_class", enriched.columns)
        self.assertIn("habitability_zone_est", enriched.columns)
        self.assertIn("calc_density", enriched.columns)

        trappist_row = enriched[enriched["pl_name"] == "TRAPPIST-1 e"].iloc[0]
        self.assertEqual(trappist_row["planet_class"], "Terrestrial")
        self.assertEqual(trappist_row["habitability_zone_est"], "Conservative Habitable Zone")
        self.assertAlmostEqual(float(trappist_row["calc_density"]), 4.90, places=1)

        kepler_row = enriched[enriched["pl_name"] == "Kepler-22 b"].iloc[0]
        self.assertEqual(kepler_row["planet_class"], "Sub-Neptune")
        self.assertEqual(kepler_row["habitability_zone_est"], "Conservative Habitable Zone")

        hd_row = enriched[enriched["pl_name"] == "HD 209458 b"].iloc[0]
        self.assertEqual(hd_row["planet_class"], "Gas Giant")
        self.assertEqual(hd_row["habitability_zone_est"], "Hot Zone")

    def test_clean_dataframe_end_to_end(self):
        """Test full clean_dataframe pipeline and metadata report."""
        cleaned_df, metadata = clean_dataframe(self.sample_data)

        self.assertEqual(metadata["input_rows"], 4)
        self.assertEqual(metadata["output_rows"], 3)
        self.assertEqual(metadata["rows_removed"], 1)
        self.assertIn("domain_completeness", metadata)
        self.assertIn("planet_classification_distribution", metadata)
        self.assertIn("actions_performed", metadata)
        self.assertGreater(metadata["completeness_overall_pct"], 0)


if __name__ == "__main__":
    unittest.main()

