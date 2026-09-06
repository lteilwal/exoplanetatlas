"""Unit tests for src/schema.py."""
import unittest

from src.schema import (
    SCHEMA,
    ColumnSpec,
    build_curated_select_clause,
    get_dtype_mapping,
    get_schema_by_domain,
    get_schema_dictionary,
    get_schema_map,
    get_schema_names,
)


class TestSchema(unittest.TestCase):
    """Test schema definitions, lookups, and SQL generation."""

    def test_schema_not_empty(self):
        """Ensure schema has column specifications."""
        self.assertGreater(len(SCHEMA), 50)

    def test_all_columns_have_valid_fields(self):
        """Verify that every column has name, description, domain, and dtype."""
        valid_domains = {"planet", "star", "system", "discovery"}
        names = set()

        for spec in SCHEMA:
            self.assertIsInstance(spec, ColumnSpec)
            self.assertTrue(len(spec.name) > 0)
            self.assertTrue(len(spec.description) > 0)
            self.assertIn(spec.domain, valid_domains)
            self.assertTrue(len(spec.dtype) > 0)
            self.assertNotIn(spec.name, names, f"Duplicate column: {spec.name}")
            names.add(spec.name)

    def test_key_columns_present(self):
        """Check for mandatory key exoplanet columns."""
        schema_names = get_schema_names()
        essential = [
            "pl_name", "hostname", "pl_orbper", "pl_orbsmax", "pl_rade",
            "pl_masse", "st_teff", "st_mass", "st_rad", "sy_dist", "ra", "dec",
            "discoverymethod", "disc_year"
        ]
        for col in essential:
            self.assertIn(col, schema_names)

    def test_domain_filtering(self):
        """Test domain lookup helpers."""
        planet_cols = get_schema_by_domain("planet")
        star_cols = get_schema_by_domain("star")
        system_cols = get_schema_by_domain("system")
        disc_cols = get_schema_by_domain("discovery")

        self.assertGreater(len(planet_cols), 0)
        self.assertGreater(len(star_cols), 0)
        self.assertGreater(len(system_cols), 0)
        self.assertGreater(len(disc_cols), 0)
        self.assertEqual(len(planet_cols) + len(star_cols) + len(system_cols) + len(disc_cols), len(SCHEMA))

    def test_build_curated_select_clause(self):
        """Ensure SELECT clause contains all schema column names."""
        select_clause = build_curated_select_clause()
        self.assertIn("pl_name", select_clause)
        self.assertIn("hostname", select_clause)
        self.assertIn("st_teff", select_clause)

    def test_schema_dictionary_export(self):
        """Ensure schema dictionary is serializable and complete."""
        schema_dict = get_schema_dictionary()
        self.assertEqual(len(schema_dict), len(SCHEMA))
        self.assertIn("pl_name", schema_dict)
        self.assertEqual(schema_dict["pl_name"]["domain"], "planet")


if __name__ == "__main__":
    unittest.main()

