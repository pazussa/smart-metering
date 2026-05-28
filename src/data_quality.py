from __future__ import annotations

import pandas as pd


def validate_asset_relationships(
    feeders: pd.DataFrame,
    transformers: pd.DataFrame,
    meters: pd.DataFrame,
) -> list[str]:
    errors: list[str] = []

    duplicated_feeders = feeders["feeder_id"].duplicated().sum()
    duplicated_transformers = transformers["transformer_id"].duplicated().sum()
    duplicated_meters = meters["meter_id"].duplicated().sum()
    if duplicated_feeders:
        errors.append(f"Duplicated feeders: {duplicated_feeders}")
    if duplicated_transformers:
        errors.append(f"Duplicated transformers: {duplicated_transformers}")
    if duplicated_meters:
        errors.append(f"Duplicated meters: {duplicated_meters}")

    missing_feeders = set(transformers["feeder_id"]) - set(feeders["feeder_id"])
    if missing_feeders:
        errors.append(f"Transformers reference missing feeders: {sorted(missing_feeders)}")

    missing_transformers = set(meters["transformer_id"]) - set(transformers["transformer_id"])
    if missing_transformers:
        errors.append(f"Meters reference missing transformers: {sorted(missing_transformers)}")

    for frame_name, frame in [
        ("feeders", feeders),
        ("transformers", transformers),
        ("meters", meters),
    ]:
        if not frame["lat"].between(-90, 90).all():
            errors.append(f"{frame_name} contains invalid latitude")
        if not frame["lon"].between(-180, 180).all():
            errors.append(f"{frame_name} contains invalid longitude")

    return errors


def validate_readings(readings: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = {"meter_id", "reading_timestamp", "energy_kwh", "voltage_v", "power_factor"}
    missing = required - set(readings.columns)
    if missing:
        return [f"Missing reading columns: {sorted(missing)}"]

    if readings.duplicated(["meter_id", "reading_timestamp"]).any():
        errors.append("Duplicate meter readings for the same timestamp")
    if (readings["energy_kwh"] < 0).any():
        errors.append("Negative energy values detected")
    if not readings["voltage_v"].between(80, 160).all():
        errors.append("Voltage values outside expected synthetic range")
    if not readings["power_factor"].between(0, 1).all():
        errors.append("Power factor values outside [0, 1]")
    return errors


def data_quality_summary(
    readings: pd.DataFrame,
    expected_readings: int,
) -> dict[str, float | int]:
    received = int(len(readings))
    missing = max(int(expected_readings) - received, 0)
    anomalies = int((readings.get("quality_flag", pd.Series(dtype=str)) == "ANOMALY").sum())
    availability = 0.0 if expected_readings <= 0 else (received / expected_readings) * 100
    return {
        "expected_readings": int(expected_readings),
        "received_readings": received,
        "missing_readings": missing,
        "anomalous_readings": anomalies,
        "availability_percent": round(availability, 4),
    }
