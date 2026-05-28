from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import SETTINGS, SYNTHETIC_DIR


def apply_meter_outage(
    readings: pd.DataFrame,
    meter_ids: list[str],
    start: str,
    end: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    readings = readings.copy()
    readings["reading_timestamp"] = pd.to_datetime(readings["reading_timestamp"])
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    outage_mask = readings["meter_id"].isin(meter_ids) & readings["reading_timestamp"].between(
        start_ts, end_ts
    )
    removed = readings.loc[outage_mask].copy()
    remaining = readings.loc[~outage_mask].copy()
    events = pd.DataFrame(
        [
            {
                "meter_id": row.meter_id,
                "event_timestamp": row.reading_timestamp,
                "event_type": "COMMUNICATION_OUTAGE",
                "event_description": "Synthetic outage injected after generation.",
                "severity": "HIGH",
            }
            for row in removed.itertuples(index=False)
        ]
    )
    return remaining, events


def inject_random_outage(
    synthetic_dir: str | Path = SYNTHETIC_DIR,
    affected_meters: int = 2,
    outage_hours: int = 6,
    seed: int = SETTINGS.random_seed,
) -> pd.DataFrame:
    synthetic_path = Path(synthetic_dir)
    readings_file = synthetic_path / "readings.csv"
    events_file = synthetic_path / "communication_events.csv"
    readings = pd.read_csv(readings_file)
    timestamps = pd.to_datetime(readings["reading_timestamp"])
    rng = np.random.default_rng(seed)
    meter_ids = sorted(readings["meter_id"].unique())
    selected = list(rng.choice(meter_ids, size=min(affected_meters, len(meter_ids)), replace=False))
    max_start_offset = max(len(timestamps.unique()) - outage_hours, 1)
    start = timestamps.min() + pd.Timedelta(hours=int(rng.integers(0, max_start_offset)))
    end = start + pd.Timedelta(hours=outage_hours - 1)
    remaining, new_events = apply_meter_outage(readings, selected, str(start), str(end))
    remaining.to_csv(readings_file, index=False)

    if events_file.exists():
        existing = pd.read_csv(events_file)
        events = pd.concat([existing, new_events], ignore_index=True)
    else:
        events = new_events
    events.to_csv(events_file, index=False)
    return new_events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inject synthetic communication outages.")
    parser.add_argument("--affected-meters", type=int, default=2)
    parser.add_argument("--outage-hours", type=int, default=6)
    parser.add_argument("--seed", type=int, default=SETTINGS.random_seed)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events = inject_random_outage(
        affected_meters=args.affected_meters,
        outage_hours=args.outage_hours,
        seed=args.seed,
    )
    print(f"Injected {len(events)} outage events.")


if __name__ == "__main__":
    main()
