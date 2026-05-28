from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"
MAPS_DIR = BASE_DIR / "maps"
SQL_DIR = BASE_DIR / "sql"
OPENDSS_DIR = BASE_DIR / "opendss"


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://smart:smartpass@localhost:5432/smart_metering",
    )
    mqtt_host: str = os.getenv("MQTT_HOST", "localhost")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    api_backend: str = os.getenv("SMART_METERING_API_BACKEND", "db").lower()
    random_seed: int = int(os.getenv("SMART_METERING_RANDOM_SEED", "20260101"))


SETTINGS = Settings()


def ensure_project_dirs() -> None:
    for directory in [RAW_DIR, SYNTHETIC_DIR, PROCESSED_DIR, MAPS_DIR, SQL_DIR, OPENDSS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def synthetic_path(filename: str) -> Path:
    ensure_project_dirs()
    return SYNTHETIC_DIR / filename


def processed_path(filename: str) -> Path:
    ensure_project_dirs()
    return PROCESSED_DIR / filename
