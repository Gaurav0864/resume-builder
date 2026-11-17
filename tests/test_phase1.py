"""Focused tests for Phase 1's local setup and safety defaults."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

import run


class PhaseOneTests(unittest.TestCase):
    """Check local storage works and its application status is constrained."""

    def test_database_can_be_initialized_more_than_once(self) -> None:
        """Repeated setup is safe and starts with no records."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "data" / "jobs.db"
            run.initialize_database(database_path)
            run.initialize_database(database_path)
            self.assertEqual(run.database_counts(database_path), (0, 0))

    def test_database_checks_application_status(self) -> None:
        """Application records use only the supported statuses."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "jobs.db"
            run.initialize_database(database_path)
            with sqlite3.connect(database_path) as connection:
                connection.execute(
                    "INSERT INTO jobs (title, company, url) VALUES (?, ?, ?)",
                    ("Junior Analyst", "Example Co", "https://example.com/job/1"),
                )
                connection.execute("INSERT INTO applications (job_id) VALUES (1)")
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO applications (job_id, status) VALUES (1, 'submitted')"
                    )
            self.assertEqual(run.database_counts(database_path), (1, 1))

    def test_default_settings_are_safe_for_pune_fresher(self) -> None:
        """Fresh setup starts in dry-run mode with the requested role targets."""
        config = run.default_config()
        self.assertIs(config["safety"]["dry_run"], True)
        self.assertEqual(config["profile"]["city"], "Pune")
        self.assertIn("Data Analyst", config["profile"]["target_roles"])


if __name__ == "__main__":
    unittest.main()
