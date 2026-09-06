"""Unit tests for Alembic database migrations."""
import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from src.core.config import REPO_ROOT


class TestAlembicMigrations(unittest.TestCase):
    """Test applying and rolling back Alembic migrations."""

    def test_migration_upgrade_and_downgrade(self):
        """Test full migration upgrade and downgrade cycle on clean database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db_path = f.name

        engine = None
        try:
            db_url = f"sqlite:///{temp_db_path}"

            # Configure Alembic
            alembic_cfg = Config(str(REPO_ROOT / "alembic.ini"))
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)

            # 1. Upgrade to head
            command.upgrade(alembic_cfg, "head")

            # Inspect created tables
            engine = create_engine(db_url)
            inspector = inspect(engine)
            tables = set(inspector.get_table_names())

            self.assertIn("systems", tables)
            self.assertIn("stars", tables)
            self.assertIn("planets", tables)
            self.assertIn("discoveries", tables)

            # 2. Downgrade to base
            command.downgrade(alembic_cfg, "base")

            # Verify tables dropped
            inspector_after = inspect(engine)
            tables_after = set(inspector_after.get_table_names())
            self.assertNotIn("planets", tables_after)
            self.assertNotIn("systems", tables_after)

        finally:
            if engine:
                engine.dispose()
            Path(temp_db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

