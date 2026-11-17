"""Local-only Phase 1 foundation for job-copilot."""

import logging
import sqlite3
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.yaml"
ENV_PATH = ROOT / ".env"


def default_config() -> dict[str, Any]:
    """Return safe starter settings for a fresher searching for jobs in Pune."""
    return {
        "profile": {
            "name": "",
            "city": "Pune",
            "target_roles": ["Data Analyst", "Junior Analyst"],
        },
        "safety": {"dry_run": True, "daily_application_cap": 25},
        "storage": {"database_path": "data/job_copilot.db"},
        "logging": {"level": "INFO", "file_path": "logs/job-copilot.log"},
    }


def write_config(config: dict[str, Any]) -> None:
    """Save configuration as readable YAML in the project folder."""
    with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
        yaml.safe_dump(config, config_file, sort_keys=False, allow_unicode=True)


def create_env_file() -> None:
    """Create an empty optional integrations file without overwriting local keys."""
    if ENV_PATH.exists():
        return
    ENV_PATH.write_text(
        "# Optional integrations can add keys here later.\n"
        "# Never put passwords in this file.\n"
        "OPENAI_API_KEY=\n",
        encoding="utf-8",
    )


def ask_with_default(question: str, default: str) -> str:
    """Ask a setup question and use its suggested value when the answer is blank."""
    answer = input(f"{question} [{default}]: ").strip()
    return answer or default


def run_first_run_wizard() -> dict[str, Any]:
    """Ask for basic profile preferences and create config.yaml and .env."""
    config = default_config()
    print("\nWelcome to job-copilot setup.")
    print("Press Enter to accept a suggested value; you can edit config.yaml later.")
    config["profile"]["name"] = ask_with_default("Your name (optional)", "")
    config["profile"]["city"] = ask_with_default("Search city", "Pune")
    role_text = ask_with_default(
        "Target roles, separated by commas", "Data Analyst, Junior Analyst"
    )
    config["profile"]["target_roles"] = [
        role.strip() for role in role_text.split(",") if role.strip()
    ] or ["Data Analyst", "Junior Analyst"]
    write_config(config)
    create_env_file()
    print("Created config.yaml and .env. No passwords were requested or saved.")
    return config


def load_config() -> dict[str, Any]:
    """Load settings and stop with a helpful message when the YAML is invalid."""
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    except yaml.YAMLError as error:
        raise ValueError(
            "config.yaml is not valid YAML. Check its spacing and punctuation."
        ) from error
    if not isinstance(config, dict):
        raise ValueError("config.yaml must contain a YAML settings map.")
    for section in ("profile", "safety", "storage", "logging"):
        if not isinstance(config.get(section), dict):
            raise ValueError(f"config.yaml needs a '{section}' settings section.")
    if config["safety"].get("dry_run") is not True:
        raise ValueError(
            "Phase 1 requires safety.dry_run: true. This tool does not submit applications."
        )
    if not isinstance(config["storage"].get("database_path"), str):
        raise ValueError("storage.database_path must be a file path in config.yaml.")
    if not isinstance(config["logging"].get("file_path"), str):
        raise ValueError("logging.file_path must be a file path in config.yaml.")
    return config


def project_path(configured_path: str) -> Path:
    """Resolve a configured local path relative to the project folder."""
    path = Path(configured_path)
    return path if path.is_absolute() else ROOT / path


def setup_logging(config: dict[str, Any]) -> logging.Logger:
    """Write readable console logs and small rotating log files."""
    log_path = project_path(config["logging"]["file_path"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("job_copilot")
    logger.setLevel(getattr(logging, str(config["logging"].get("level", "INFO")).upper(), logging.INFO))
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def initialize_database(database_path: Path) -> None:
    """Create the local SQLite database and starter jobs/applications tables."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'manual',
                url TEXT NOT NULL UNIQUE,
                discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                status TEXT NOT NULL DEFAULT 'found'
                    CHECK (status IN ('found', 'reviewed', 'applied', 'interview', 'rejected')),
                notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def database_counts(database_path: Path) -> tuple[int, int]:
    """Return saved-job and application counts from the local database."""
    with sqlite3.connect(database_path) as connection:
        jobs = connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        applications = connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    return jobs, applications


def show_status(config: dict[str, Any]) -> None:
    """Show safe dry-run status and local record counts."""
    database_path = project_path(config["storage"]["database_path"])
    initialize_database(database_path)
    jobs, applications = database_counts(database_path)
    print("\nDry-run mode: ON (safe; no applications will be submitted)")
    print(f"Saved jobs: {jobs}")
    print(f"Application records: {applications}")
    print(f"Local database: {database_path}")


def show_settings(config: dict[str, Any]) -> None:
    """Display profile preferences without showing any secret values."""
    profile = config["profile"]
    safety = config["safety"]
    print("\nCurrent settings")
    print(f"Name: {profile.get('name') or '(not set)'}")
    print(f"City: {profile.get('city', 'Pune')}")
    print(f"Target roles: {', '.join(profile.get('target_roles', []))}")
    print("Dry-run mode: ON")
    print(f"Daily application cap setting: {safety.get('daily_application_cap', 25)}")


def show_menu() -> None:
    """Print the numbered Phase 1 menu."""
    print("\n=== job-copilot | Phase 1 ===")
    print("1. Show project status")
    print("2. View settings")
    print("3. Confirm dry-run mode is ON")
    print("4. Initialize local database")
    print("0. Exit")


def main() -> int:
    """Set up the local app and respond to numbered menu choices."""
    try:
        config = run_first_run_wizard() if not CONFIG_PATH.exists() else load_config()
        create_env_file()
        logger = setup_logging(config)
    except (OSError, ValueError) as error:
        print(f"Setup problem: {error}")
        return 1

    logger.info("job-copilot Phase 1 started in dry-run mode")
    while True:
        show_menu()
        try:
            choice = input("Choose a number: ").strip()
        except EOFError:
            print("\nNo input received. Exiting safely.")
            return 0
        try:
            if choice == "1":
                show_status(config)
            elif choice == "2":
                show_settings(config)
            elif choice == "3":
                print("Dry-run mode is ON. This phase only prepares locally.")
            elif choice == "4":
                database_path = project_path(config["storage"]["database_path"])
                initialize_database(database_path)
                print(f"Local database is ready: {database_path}")
            elif choice == "0":
                logger.info("User exited the menu")
                print("Goodbye. No applications were submitted.")
                return 0
            else:
                print("Please enter one of the numbers shown in the menu.")
        except (OSError, sqlite3.Error) as error:
            logger.exception("A menu action failed")
            print(f"Could not complete that action: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
