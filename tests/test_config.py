"""Unit tests for src/config.py."""
import unittest
from pathlib import Path

from src import config


class TestConfig(unittest.TestCase):
    """Test configuration paths and settings."""

    def test_paths_defined(self):
        """Ensure all required paths are defined and point to expected directories."""
        self.assertIsInstance(config.PROJECT_ROOT, Path)
        self.assertIsInstance(config.DATA_DIR, Path)
        self.assertIsInstance(config.RAW_DATA_DIR, Path)
        self.assertIsInstance(config.PROCESSED_DATA_DIR, Path)
        self.assertIsInstance(config.LOGS_DIR, Path)
        self.assertIsInstance(config.RAW_CSV_FILE, Path)
        self.assertIsInstance(config.PROCESSED_PLANETS_FILE, Path)
        self.assertIsInstance(config.PROCESSED_METADATA_FILE, Path)
        self.assertIsInstance(config.DATA_DICTIONARY_FILE, Path)

    def test_tap_constants(self):
        """Ensure TAP constants are valid strings."""
        self.assertTrue(config.NASA_TAP_URL.startswith("https://"))
        self.assertEqual(config.DEFAULT_TABLE, "pscomppars")
        self.assertGreater(config.HTTP_TIMEOUT_SECONDS, 0)
        self.assertGreaterEqual(config.HTTP_RETRIES, 0)

    def test_ensure_directories(self):
        """Ensure directories are created without error."""
        config.ensure_directories()
        self.assertTrue(config.DATA_DIR.exists())
        self.assertTrue(config.RAW_DATA_DIR.exists())
        self.assertTrue(config.PROCESSED_DATA_DIR.exists())
        self.assertTrue(config.LOGS_DIR.exists())


if __name__ == "__main__":
    unittest.main()

