from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import PROCESSED_DIR, SYNTHETIC_DIR, ensure_project_dirs
from src.generate_synthetic_readings import coerce_bool

BALANCE_COLUMNS = [
    "transformer_id",
    "reading_timestamp",
    "input_energy_kwh",
    "measured_energy_kwh",
    "loss_kwh",
    "loss_percent",
    "expected_readings",
    "received_readings",
    "reading_availability_percent",
]


def calculate_loss(input_energy_kwh: float, measured_energy_kwh: float) -> tuple[float, float]:
    loss_kwh = float(input_energy_kwh) - float(measured_energy_kwh)
    if input_energy_kwh <= 0:
        return loss_kwh, 0.0
    return loss_kwh, (loss_kwh / float(input_energy_kwh)) * 100


def calculate_availability(expected_readings: int, received_readings: int) -> float:
    if expected_readings <= 0:
        return 0.0
    return (float(received_readings) / float(expected_readings)) * 100


def calculate_energy_balance_from_frames(
    meters: pd.DataFrame,
    readings: pd.DataFrame,
    macro_readings: pd.DataFrame,
) -> pd.DataFrame:
    if meters.empty:
        raise ValueError("meters dataframe is empty")
    if macro_readings.empty:
        raise ValueError("macro_readings dataframe is empty")

    meters = meters.copy()
    readings = readings.copy()
    macro = macro_readings.copy()

    meters["is_macro"] = coerce_bool(meters["is_macro"])
    smart_meters = meters.loc[~meters["is_macro"], ["meter_id", "transformer_id"]].copy()
    if smart_meters.empty:
        raise ValueError("No downstream smart meters available for balance calculation.")

    if not readings.empty:
        readings["reading_timestamp"] = pd.to_datetime(readings["reading_timestamp"])
        readings = readings.merge(smart_meters, on="meter_id", how="inner")
        measured = readings.groupby(["transformer_id", "reading_timestamp"], as_index=False).agg(
            measured_energy_kwh=("energy_kwh", "sum"),
            received_readings=("meter_id", "count"),
        )
    else:
        measured = pd.DataFrame(
            columns=[
                "transformer_id",
                "reading_timestamp",
                "measured_energy_kwh",
                "received_readings",
            ]
        )

    expected = smart_meters.groupby("transformer_id", as_index=False).agg(
        expected_readings=("meter_id", "count")
    )

    macro["reading_timestamp"] = pd.to_datetime(macro["reading_timestamp"])
    balance = macro.merge(measured, on=["transformer_id", "reading_timestamp"], how="left")
    balance = balance.merge(expected, on="transformer_id", how="left")

    balance["measured_energy_kwh"] = balance["measured_energy_kwh"].fillna(0.0).astype(float)
    balance["received_readings"] = balance["received_readings"].fillna(0).astype(int)
    balance["expected_readings"] = balance["expected_readings"].fillna(0).astype(int)
    balance["input_energy_kwh"] = balance["input_energy_kwh"].astype(float)
    balance["loss_kwh"] = balance["input_energy_kwh"] - balance["measured_energy_kwh"]
    balance["loss_percent"] = np.where(
        balance["input_energy_kwh"] > 0,
        (balance["loss_kwh"] / balance["input_energy_kwh"]) * 100,
        0.0,
    )
    balance["reading_availability_percent"] = np.where(
        balance["expected_readings"] > 0,
        (balance["received_readings"] / balance["expected_readings"]) * 100,
        0.0,
    )

    for column in [
        "input_energy_kwh",
        "measured_energy_kwh",
        "loss_kwh",
        "loss_percent",
        "reading_availability_percent",
    ]:
        balance[column] = balance[column].round(4)

    return (
        balance[BALANCE_COLUMNS]
        .sort_values(["transformer_id", "reading_timestamp"])
        .reset_index(drop=True)
    )


def calculate_energy_balance(
    input_dir: str | Path = SYNTHETIC_DIR,
    output_dir: str | Path = PROCESSED_DIR,
) -> pd.DataFrame:
    ensure_project_dirs()
    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    meters = pd.read_csv(in_dir / "meters.csv")
    readings = pd.read_csv(in_dir / "readings.csv")
    macro = pd.read_csv(in_dir / "macro_readings.csv")
    balance = calculate_energy_balance_from_frames(meters, readings, macro)
    balance.to_csv(out_dir / "energy_balance.csv", index=False)
    return balance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate transformer energy balances.")
    parser.add_argument("--input-dir", default=str(SYNTHETIC_DIR))
    parser.add_argument("--output-dir", default=str(PROCESSED_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    balance = calculate_energy_balance(args.input_dir, args.output_dir)
    print(balance.head().to_string(index=False))
    print(f"Generated {len(balance)} balance rows.")


if __name__ == "__main__":
    main()
