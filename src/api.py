from __future__ import annotations

import os
from typing import Any

import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine, text

from src.config import PROCESSED_DIR, SETTINGS

app = FastAPI(title="Smart Metering Loss Analysis API", version="1.0.0")


def _json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    clean = frame.copy()
    for column in clean.columns:
        if pd.api.types.is_datetime64_any_dtype(clean[column]):
            clean[column] = clean[column].dt.strftime("%Y-%m-%dT%H:%M:%S")
    clean = clean.where(pd.notna(clean), None)
    return clean.to_dict(orient="records")


def _engine():
    return create_engine(SETTINGS.database_url, future=True)


def _use_csv_backend() -> bool:
    return os.getenv("SMART_METERING_API_BACKEND", SETTINGS.api_backend).lower() == "csv"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/balances/latest")
def latest_balances() -> list[dict[str, Any]]:
    if _use_csv_backend():
        balance_file = PROCESSED_DIR / "energy_balance.csv"
        balance = pd.read_csv(balance_file, parse_dates=["reading_timestamp"])
        latest = balance.sort_values("reading_timestamp").groupby("transformer_id").tail(1)
        latest = latest.sort_values("loss_percent", ascending=False)
        return _json_records(latest)

    query = """
        SELECT transformer_id, transformer_name, sector, reading_timestamp,
               input_energy_kwh, measured_energy_kwh, loss_kwh,
               loss_percent, reading_availability_percent
        FROM v_transformer_latest_balance
        ORDER BY loss_percent DESC
    """
    with _engine().begin() as connection:
        rows = connection.execute(text(query)).mappings().all()
    return [dict(row) for row in rows]


@app.get("/alerts/open")
def open_alerts() -> list[dict[str, Any]]:
    if _use_csv_backend():
        alerts_file = PROCESSED_DIR / "alerts.csv"
        if not alerts_file.exists():
            return []
        alerts = pd.read_csv(alerts_file, parse_dates=["alert_timestamp"])
        if "status" in alerts:
            alerts = alerts.loc[alerts["status"] == "OPEN"]
        return _json_records(alerts.sort_values("alert_timestamp", ascending=False))

    query = """
        SELECT entity_type, entity_id, alert_timestamp,
               alert_type, alert_message, severity, status
        FROM v_open_alerts
        ORDER BY alert_timestamp DESC
    """
    with _engine().begin() as connection:
        rows = connection.execute(text(query)).mappings().all()
    return [dict(row) for row in rows]
