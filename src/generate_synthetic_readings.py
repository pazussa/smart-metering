from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import SETTINGS, SYNTHETIC_DIR, ensure_project_dirs


def coerce_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def customer_base_load(customer_type: str, rng: np.random.Generator) -> float:
    if customer_type == "RESIDENTIAL":
        return float(rng.uniform(0.25, 1.8))
    if customer_type == "COMMERCIAL":
        return float(rng.uniform(1.2, 5.5))
    if customer_type == "SMALL_INDUSTRY":
        return float(rng.uniform(3.5, 12.0))
    return float(rng.uniform(0.5, 2.0))


def daily_profile_multiplier(hour: int) -> float:
    if 0 <= hour <= 5:
        return 0.45
    if 6 <= hour <= 8:
        return 0.85
    if 9 <= hour <= 17:
        return 1.00
    if 18 <= hour <= 22:
        return 1.35
    return 0.75


def weekday_multiplier(timestamp: pd.Timestamp) -> float:
    return 0.92 if timestamp.weekday() >= 5 else 1.0


def build_reading_record(
    meter_id: str,
    timestamp: pd.Timestamp,
    energy_kwh: float,
    rng: np.random.Generator,
    quality_flag: str = "OK",
) -> dict[str, object]:
    return {
        "meter_id": meter_id,
        "reading_timestamp": timestamp,
        "energy_kwh": round(max(float(energy_kwh), 0.01), 4),
        "voltage_v": round(float(np.clip(rng.normal(120, 4), 105, 132)), 2),
        "current_a": round(float(max(rng.normal(12, 3), 0.2)), 2),
        "power_factor": round(float(np.clip(rng.normal(0.93, 0.03), 0.7, 1.0)), 3),
        "quality_flag": quality_flag,
        "source": "synthetic",
    }


def generate_readings(
    days: int = 30,
    seed: int = SETTINGS.random_seed,
    start: str = "2026-01-01 00:00:00",
    missing_probability: float = 0.03,
    anomaly_probability: float = 0.01,
    loss_factor_range: tuple[float, float] = (0.04, 0.18),
    input_dir: str | Path = SYNTHETIC_DIR,
    output_dir: str | Path = SYNTHETIC_DIR,
    meters: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    if days <= 0:
        raise ValueError("days must be greater than zero")
    if not 0 <= missing_probability < 1:
        raise ValueError("missing_probability must be in [0, 1)")
    if not 0 <= anomaly_probability < 1:
        raise ValueError("anomaly_probability must be in [0, 1)")
    low_loss, high_loss = loss_factor_range
    if not 0 <= low_loss <= high_loss < 1:
        raise ValueError("loss_factor_range must contain values in [0, 1)")

    ensure_project_dirs()
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    if meters is None:
        meters = pd.read_csv(in_dir / "meters.csv")
    meters = meters.copy()
    meters["is_macro"] = coerce_bool(meters["is_macro"])
    smart_meters = meters.loc[~meters["is_macro"]].copy()
    if smart_meters.empty:
        raise ValueError("No smart meters found. Generate assets first.")

    timestamps = pd.date_range(start, periods=days * 24, freq="h")
    base_load_by_meter = {
        row.meter_id: customer_base_load(row.customer_type, rng)
        for row in smart_meters.itertuples(index=False)
    }

    readings: list[dict[str, object]] = []
    macro_rows: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    true_energy: dict[tuple[str, pd.Timestamp], float] = {}

    for row in smart_meters.itertuples(index=False):
        base_load = base_load_by_meter[row.meter_id]
        for ts in timestamps:
            energy = (
                base_load
                * daily_profile_multiplier(ts.hour)
                * weekday_multiplier(ts)
                * float(np.clip(rng.normal(1.0, 0.10), 0.55, 1.55))
            )
            key = (row.transformer_id, ts)
            true_energy[key] = true_energy.get(key, 0.0) + energy

            if rng.random() < missing_probability:
                events.append(
                    {
                        "meter_id": row.meter_id,
                        "event_timestamp": ts,
                        "event_type": "MISSING_READING",
                        "event_description": "Synthetic communication gap; reading not received.",
                        "severity": "MEDIUM",
                    }
                )
                continue

            quality_flag = "OK"
            recorded_energy = energy
            if rng.random() < anomaly_probability:
                recorded_energy *= float(rng.choice([0.1, 4.5]))
                quality_flag = "ANOMALY"

            readings.append(
                build_reading_record(row.meter_id, ts, recorded_energy, rng, quality_flag)
            )

    transformer_ids = sorted(smart_meters["transformer_id"].unique())
    for transformer_id in transformer_ids:
        transformer_profile = 0.0
        for ts in timestamps:
            measured_true = true_energy.get((transformer_id, ts), 0.0)
            transformer_profile = measured_true if measured_true > 0 else transformer_profile
            loss_factor = float(rng.uniform(low_loss, high_loss))
            input_energy = (measured_true or transformer_profile) / (1 - loss_factor)
            macro_rows.append(
                {
                    "transformer_id": transformer_id,
                    "reading_timestamp": ts,
                    "input_energy_kwh": round(max(input_energy, 0.01), 4),
                    "quality_flag": "OK",
                    "source": "synthetic",
                }
            )

    frames = {
        "readings": pd.DataFrame(readings),
        "macro_readings": pd.DataFrame(macro_rows),
        "communication_events": pd.DataFrame(events),
    }
    frames["readings"].to_csv(out_dir / "readings.csv", index=False)
    frames["macro_readings"].to_csv(out_dir / "macro_readings.csv", index=False)
    frames["communication_events"].to_csv(out_dir / "communication_events.csv", index=False)
    return frames


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic smart-meter readings.")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=SETTINGS.random_seed)
    parser.add_argument("--missing-probability", type=float, default=0.03)
    parser.add_argument("--anomaly-probability", type=float, default=0.01)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frames = generate_readings(
        days=args.days,
        seed=args.seed,
        missing_probability=args.missing_probability,
        anomaly_probability=args.anomaly_probability,
    )
    print(
        "Generated readings: "
        f"{len(frames['readings'])} meter rows, "
        f"{len(frames['macro_readings'])} macro rows, "
        f"{len(frames['communication_events'])} communication events."
    )


if __name__ == "__main__":
    main()
