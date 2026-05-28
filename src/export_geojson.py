from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import MAPS_DIR, PROCESSED_DIR, SYNTHETIC_DIR, ensure_project_dirs
from src.generate_synthetic_readings import coerce_bool


def _feature(
    longitude: float,
    latitude: float,
    properties: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(longitude), float(latitude)]},
        "properties": properties,
    }


def build_assets_geojson(
    feeders: pd.DataFrame,
    transformers: pd.DataFrame,
    meters: pd.DataFrame,
    balance: pd.DataFrame | None = None,
) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    latest_loss: dict[str, dict[str, Any]] = {}

    if balance is not None and not balance.empty:
        balance = balance.copy()
        balance["reading_timestamp"] = pd.to_datetime(balance["reading_timestamp"])
        latest = balance.sort_values("reading_timestamp").groupby("transformer_id").tail(1)
        latest_loss = latest.set_index("transformer_id")[
            ["loss_percent", "reading_availability_percent", "reading_timestamp"]
        ].to_dict("index")

    for row in feeders.itertuples(index=False):
        features.append(
            _feature(
                row.lon,
                row.lat,
                {
                    "asset_type": "feeder",
                    "asset_id": row.feeder_id,
                    "name": row.name,
                    "zone": row.zone,
                    "voltage_kv": row.voltage_kv,
                },
            )
        )

    for row in transformers.itertuples(index=False):
        loss = latest_loss.get(row.transformer_id, {})
        timestamp = loss.get("reading_timestamp")
        if hasattr(timestamp, "isoformat"):
            timestamp = timestamp.isoformat()
        features.append(
            _feature(
                row.lon,
                row.lat,
                {
                    "asset_type": "transformer",
                    "asset_id": row.transformer_id,
                    "feeder_id": row.feeder_id,
                    "name": row.name,
                    "sector": row.sector,
                    "capacity_kva": row.capacity_kva,
                    "latest_loss_percent": loss.get("loss_percent"),
                    "latest_availability_percent": loss.get("reading_availability_percent"),
                    "latest_balance_timestamp": timestamp,
                },
            )
        )

    meters = meters.copy()
    meters["is_macro"] = coerce_bool(meters["is_macro"])
    for row in meters.itertuples(index=False):
        features.append(
            _feature(
                row.lon,
                row.lat,
                {
                    "asset_type": "macro_meter" if row.is_macro else "smart_meter",
                    "asset_id": row.meter_id,
                    "transformer_id": row.transformer_id,
                    "customer_type": row.customer_type,
                    "communication_type": row.communication_type,
                    "installation_status": row.installation_status,
                },
            )
        )

    return {"type": "FeatureCollection", "features": features}


def export_assets_geojson(
    synthetic_dir: str | Path = SYNTHETIC_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
    output_file: str | Path = MAPS_DIR / "assets.geojson",
) -> dict[str, Any]:
    ensure_project_dirs()
    synthetic_path = Path(synthetic_dir)
    processed_path = Path(processed_dir)

    feeders = pd.read_csv(synthetic_path / "feeders.csv")
    transformers = pd.read_csv(synthetic_path / "transformers.csv")
    meters = pd.read_csv(synthetic_path / "meters.csv")
    balance_file = processed_path / "energy_balance.csv"
    balance = pd.read_csv(balance_file) if balance_file.exists() else None

    geojson = build_assets_geojson(feeders, transformers, meters, balance)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    return geojson


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export synthetic assets to GeoJSON.")
    parser.add_argument("--output-file", default=str(MAPS_DIR / "assets.geojson"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    geojson = export_assets_geojson(output_file=args.output_file)
    print(f"Exported {len(geojson['features'])} GIS features to {args.output_file}.")


if __name__ == "__main__":
    main()
