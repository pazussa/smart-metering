from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import SETTINGS, SYNTHETIC_DIR, ensure_project_dirs

POPAYAN_LAT = 2.4448
POPAYAN_LON = -76.6147


def jitter(rng: np.random.Generator, value: float, delta: float = 0.02) -> float:
    return float(value + rng.uniform(-delta, delta))


def generate_assets(
    feeders_count: int = 2,
    transformers_per_feeder: int = 3,
    meters_per_transformer: int = 12,
    seed: int = SETTINGS.random_seed,
    output_dir: str | Path = SYNTHETIC_DIR,
) -> dict[str, pd.DataFrame]:
    if feeders_count <= 0:
        raise ValueError("feeders_count must be greater than zero")
    if transformers_per_feeder <= 0:
        raise ValueError("transformers_per_feeder must be greater than zero")
    if meters_per_transformer <= 0:
        raise ValueError("meters_per_transformer must be greater than zero")

    ensure_project_dirs()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    feeders: list[dict[str, object]] = []
    transformers: list[dict[str, object]] = []
    meters: list[dict[str, object]] = []

    customer_types = np.array(["RESIDENTIAL", "COMMERCIAL", "SMALL_INDUSTRY"])
    communication_types = np.array(["MQTT", "MODBUS_TCP", "DLMS_SIM"])
    capacities = np.array([75.0, 112.5, 150.0, 225.0])

    for feeder_number in range(1, feeders_count + 1):
        feeder_id = f"FD-{feeder_number:02d}"
        feeder_lat = jitter(rng, POPAYAN_LAT)
        feeder_lon = jitter(rng, POPAYAN_LON)
        feeders.append(
            {
                "feeder_id": feeder_id,
                "name": f"Feeder {feeder_number}",
                "voltage_kv": 13.2,
                "zone": f"Zone {feeder_number}",
                "lat": feeder_lat,
                "lon": feeder_lon,
            }
        )

        for transformer_number in range(1, transformers_per_feeder + 1):
            transformer_id = f"TR-{feeder_number:02d}-{transformer_number:02d}"
            transformer_lat = jitter(rng, feeder_lat, 0.012)
            transformer_lon = jitter(rng, feeder_lon, 0.012)
            transformers.append(
                {
                    "transformer_id": transformer_id,
                    "feeder_id": feeder_id,
                    "name": f"Transformer {feeder_number}-{transformer_number}",
                    "capacity_kva": float(rng.choice(capacities)),
                    "sector": f"S-{feeder_number}-{transformer_number}",
                    "lat": transformer_lat,
                    "lon": transformer_lon,
                }
            )

            meters.append(
                {
                    "meter_id": f"MM-{feeder_number:02d}-{transformer_number:02d}",
                    "transformer_id": transformer_id,
                    "customer_type": "MACRO",
                    "is_macro": True,
                    "communication_type": "MQTT",
                    "installation_status": "ACTIVE",
                    "lat": jitter(rng, transformer_lat, 0.0025),
                    "lon": jitter(rng, transformer_lon, 0.0025),
                }
            )

            for meter_number in range(1, meters_per_transformer + 1):
                meters.append(
                    {
                        "meter_id": (
                            f"SM-{feeder_number:02d}-{transformer_number:02d}-{meter_number:03d}"
                        ),
                        "transformer_id": transformer_id,
                        "customer_type": str(rng.choice(customer_types)),
                        "is_macro": False,
                        "communication_type": str(rng.choice(communication_types)),
                        "installation_status": "ACTIVE",
                        "lat": jitter(rng, transformer_lat, 0.006),
                        "lon": jitter(rng, transformer_lon, 0.006),
                    }
                )

    frames = {
        "feeders": pd.DataFrame(feeders),
        "transformers": pd.DataFrame(transformers),
        "meters": pd.DataFrame(meters),
    }

    for name, frame in frames.items():
        frame.to_csv(out_dir / f"{name}.csv", index=False)

    return frames


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic grid assets.")
    parser.add_argument("--feeders", type=int, default=2)
    parser.add_argument("--transformers-per-feeder", type=int, default=3)
    parser.add_argument("--meters-per-transformer", type=int, default=12)
    parser.add_argument("--seed", type=int, default=SETTINGS.random_seed)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frames = generate_assets(
        feeders_count=args.feeders,
        transformers_per_feeder=args.transformers_per_feeder,
        meters_per_transformer=args.meters_per_transformer,
        seed=args.seed,
    )
    print(
        "Generated assets: "
        f"{len(frames['feeders'])} feeders, "
        f"{len(frames['transformers'])} transformers, "
        f"{len(frames['meters'])} meters."
    )


if __name__ == "__main__":
    main()
