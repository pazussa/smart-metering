import json

import pandas as pd

from src.calculate_energy_balance import calculate_energy_balance
from src.detect_anomalies import detect_anomalies
from src.export_geojson import export_assets_geojson
from src.generate_assets import generate_assets
from src.generate_synthetic_readings import generate_readings


def test_generators_create_expected_files_and_shapes(tmp_path):
    assets = generate_assets(
        feeders_count=1,
        transformers_per_feeder=2,
        meters_per_transformer=3,
        seed=7,
        output_dir=tmp_path,
    )
    readings = generate_readings(
        days=2,
        seed=7,
        missing_probability=0.15,
        anomaly_probability=0.1,
        input_dir=tmp_path,
        output_dir=tmp_path,
        meters=assets["meters"],
    )

    assert (tmp_path / "feeders.csv").exists()
    assert (tmp_path / "transformers.csv").exists()
    assert (tmp_path / "meters.csv").exists()
    assert (tmp_path / "readings.csv").exists()
    assert (tmp_path / "macro_readings.csv").exists()
    assert (tmp_path / "communication_events.csv").exists()

    assert len(assets["feeders"]) == 1
    assert len(assets["transformers"]) == 2
    assert len(assets["meters"]) == 8
    assert len(readings["macro_readings"]) == 2 * 48
    assert set(readings["readings"]["quality_flag"]).issubset({"OK", "ANOMALY"})


def test_full_csv_pipeline_generates_balance_alerts_and_geojson(tmp_path):
    generate_assets(
        feeders_count=1,
        transformers_per_feeder=1,
        meters_per_transformer=4,
        seed=10,
        output_dir=tmp_path,
    )
    generate_readings(
        days=1,
        seed=10,
        missing_probability=0.25,
        anomaly_probability=0.25,
        input_dir=tmp_path,
        output_dir=tmp_path,
    )
    processed_dir = tmp_path / "processed"
    balance = calculate_energy_balance(input_dir=tmp_path, output_dir=processed_dir)
    alerts = detect_anomalies(
        loss_threshold_percent=1.0,
        availability_threshold_percent=100.0,
        synthetic_dir=tmp_path,
        processed_dir=processed_dir,
    )
    output_geojson = tmp_path / "assets.geojson"
    geojson = export_assets_geojson(
        synthetic_dir=tmp_path,
        processed_dir=processed_dir,
        output_file=output_geojson,
    )

    assert not balance.empty
    assert {"loss_kwh", "loss_percent", "reading_availability_percent"}.issubset(balance.columns)
    assert not alerts.empty
    assert output_geojson.exists()
    assert json.loads(output_geojson.read_text(encoding="utf-8")) == geojson
    assert len(geojson["features"]) == 1 + 1 + 5


def test_generator_is_deterministic_for_same_seed(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first = generate_assets(output_dir=first_dir, seed=123)
    second = generate_assets(output_dir=second_dir, seed=123)

    pd.testing.assert_frame_equal(first["meters"], second["meters"])
