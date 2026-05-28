from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, SYNTHETIC_DIR, ensure_project_dirs

ALERT_COLUMNS = [
    "entity_type",
    "entity_id",
    "alert_timestamp",
    "alert_type",
    "alert_message",
    "severity",
    "status",
]


def _alert(
    entity_type: str,
    entity_id: str,
    timestamp: object,
    alert_type: str,
    message: str,
    severity: str,
) -> dict[str, object]:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "alert_timestamp": timestamp,
        "alert_type": alert_type,
        "alert_message": message,
        "severity": severity,
        "status": "OPEN",
    }


def detect_alerts_from_frames(
    balance: pd.DataFrame,
    readings: pd.DataFrame,
    loss_threshold_percent: float = 12.0,
    availability_threshold_percent: float = 95.0,
    voltage_min: float = 105.0,
    voltage_max: float = 132.0,
) -> pd.DataFrame:
    alerts: list[dict[str, object]] = []

    if not balance.empty:
        balance = balance.copy()
        balance["reading_timestamp"] = pd.to_datetime(balance["reading_timestamp"])
        high_loss = balance.loc[balance["loss_percent"] > loss_threshold_percent]
        for row in high_loss.itertuples(index=False):
            alerts.append(
                _alert(
                    "TRANSFORMER",
                    row.transformer_id,
                    row.reading_timestamp,
                    "HIGH_LOSS",
                    f"Loss percent {row.loss_percent:.2f}% exceeds {loss_threshold_percent:.2f}%.",
                    "HIGH",
                )
            )

        low_availability = balance.loc[
            balance["reading_availability_percent"] < availability_threshold_percent
        ]
        for row in low_availability.itertuples(index=False):
            alerts.append(
                _alert(
                    "TRANSFORMER",
                    row.transformer_id,
                    row.reading_timestamp,
                    "LOW_READING_AVAILABILITY",
                    (
                        f"Reading availability {row.reading_availability_percent:.2f}% "
                        f"is below {availability_threshold_percent:.2f}%."
                    ),
                    "MEDIUM",
                )
            )

    if not readings.empty:
        readings = readings.copy()
        readings["reading_timestamp"] = pd.to_datetime(readings["reading_timestamp"])
        anomaly_mask = readings.get("quality_flag", "") == "ANOMALY"
        if "voltage_v" in readings:
            anomaly_mask = anomaly_mask | ~readings["voltage_v"].between(voltage_min, voltage_max)
        for row in readings.loc[anomaly_mask].itertuples(index=False):
            energy = getattr(row, "energy_kwh", None)
            alerts.append(
                _alert(
                    "METER",
                    row.meter_id,
                    row.reading_timestamp,
                    "ANOMALOUS_READING",
                    f"Anomalous reading detected: {energy} kWh.",
                    "MEDIUM",
                )
            )

    return pd.DataFrame(alerts, columns=ALERT_COLUMNS)


def detect_anomalies(
    loss_threshold_percent: float = 12.0,
    availability_threshold_percent: float = 95.0,
    synthetic_dir: str | Path = SYNTHETIC_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
) -> pd.DataFrame:
    ensure_project_dirs()
    synthetic_path = Path(synthetic_dir)
    processed_path = Path(processed_dir)
    processed_path.mkdir(parents=True, exist_ok=True)

    balance = pd.read_csv(processed_path / "energy_balance.csv")
    readings = pd.read_csv(synthetic_path / "readings.csv")
    alerts = detect_alerts_from_frames(
        balance,
        readings,
        loss_threshold_percent=loss_threshold_percent,
        availability_threshold_percent=availability_threshold_percent,
    )
    alerts.to_csv(processed_path / "alerts.csv", index=False)
    return alerts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect loss, availability and reading anomalies.")
    parser.add_argument("--loss-threshold-percent", type=float, default=12.0)
    parser.add_argument("--availability-threshold-percent", type=float, default=95.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    alerts = detect_anomalies(
        loss_threshold_percent=args.loss_threshold_percent,
        availability_threshold_percent=args.availability_threshold_percent,
    )
    print(alerts.head().to_string(index=False) if not alerts.empty else "No alerts detected.")
    print(f"Generated {len(alerts)} alerts.")


if __name__ == "__main__":
    main()
