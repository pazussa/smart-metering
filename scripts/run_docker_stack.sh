#!/usr/bin/env bash
set -euo pipefail

COMPOSE="docker-compose"
if ! command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker compose"
fi

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

"$PYTHON_BIN" -m src.doctor --require-docker
"$PYTHON_BIN" -m src.generate_assets
"$PYTHON_BIN" -m src.generate_synthetic_readings --days "${SMART_METERING_DAYS:-7}"
"$PYTHON_BIN" -m src.calculate_energy_balance
"$PYTHON_BIN" -m src.detect_anomalies
"$PYTHON_BIN" -m src.export_geojson

$COMPOSE up -d --build

"$PYTHON_BIN" - <<'PY'
import time
from sqlalchemy import create_engine, text
from src.config import SETTINGS

engine = create_engine(SETTINGS.database_url, future=True)
deadline = time.time() + 90
last_error = None
while time.time() < deadline:
    try:
        with engine.begin() as connection:
            connection.execute(text("SELECT 1"))
        print("PostgreSQL is reachable")
        break
    except Exception as exc:
        last_error = exc
        time.sleep(3)
else:
    raise SystemExit(f"PostgreSQL did not become reachable: {last_error}")
PY

"$PYTHON_BIN" -m src.database_loader --reset
"$PYTHON_BIN" -m src.database_smoke_test
"$PYTHON_BIN" -m src.mqtt_smoke_test
"$PYTHON_BIN" -m pytest

"$PYTHON_BIN" - <<'PY'
import json
import time
import urllib.request


def fetch_json(path):
    with urllib.request.urlopen(f"http://127.0.0.1:8000{path}", timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


deadline = time.time() + 60
last_error = None
while time.time() < deadline:
    try:
        health = fetch_json("/health")
        balances = fetch_json("/balances/latest")
        alerts = fetch_json("/alerts/open")
        assert health["status"] == "ok"
        assert len(balances) > 0
        print("API DB smoke:", len(balances), "latest balances,", len(alerts), "open alerts")
        break
    except Exception as exc:
        last_error = exc
        time.sleep(2)
else:
    raise SystemExit(f"API did not become ready: {last_error}")
PY

$COMPOSE ps
