#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

"$PYTHON_BIN" -m src.doctor
"$PYTHON_BIN" -m src.generate_assets
"$PYTHON_BIN" -m src.generate_synthetic_readings --days "${SMART_METERING_DAYS:-7}"
"$PYTHON_BIN" -m src.calculate_energy_balance
"$PYTHON_BIN" -m src.detect_anomalies
"$PYTHON_BIN" -m src.export_geojson
"$PYTHON_BIN" -m pytest

SMART_METERING_API_BACKEND=csv "$PYTHON_BIN" - <<'PY'
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)
assert client.get("/health").status_code == 200
balances = client.get("/balances/latest")
alerts = client.get("/alerts/open")
assert balances.status_code == 200
assert alerts.status_code == 200
print("API CSV smoke:", len(balances.json()), "latest balances,", len(alerts.json()), "open alerts")
PY
