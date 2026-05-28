import pandas as pd

from src.data_quality import data_quality_summary, validate_asset_relationships, validate_readings


def test_validate_asset_relationships_passes_for_consistent_assets():
    feeders = pd.DataFrame([{"feeder_id": "FD-01", "lat": 2.44, "lon": -76.61}])
    transformers = pd.DataFrame(
        [{"transformer_id": "TR-01", "feeder_id": "FD-01", "lat": 2.45, "lon": -76.62}]
    )
    meters = pd.DataFrame(
        [{"meter_id": "SM-01", "transformer_id": "TR-01", "lat": 2.46, "lon": -76.63}]
    )

    assert validate_asset_relationships(feeders, transformers, meters) == []


def test_validate_asset_relationships_reports_orphans():
    feeders = pd.DataFrame([{"feeder_id": "FD-01", "lat": 2.44, "lon": -76.61}])
    transformers = pd.DataFrame(
        [{"transformer_id": "TR-01", "feeder_id": "FD-404", "lat": 2.45, "lon": -76.62}]
    )
    meters = pd.DataFrame(
        [{"meter_id": "SM-01", "transformer_id": "TR-404", "lat": 2.46, "lon": -76.63}]
    )

    errors = validate_asset_relationships(feeders, transformers, meters)

    assert any("missing feeders" in error for error in errors)
    assert any("missing transformers" in error for error in errors)


def test_validate_readings_detects_duplicates_and_invalid_ranges():
    readings = pd.DataFrame(
        [
            {
                "meter_id": "SM-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": -1.0,
                "voltage_v": 200.0,
                "power_factor": 1.2,
            },
            {
                "meter_id": "SM-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": 1.0,
                "voltage_v": 120.0,
                "power_factor": 0.9,
            },
        ]
    )

    errors = validate_readings(readings)

    assert "Duplicate meter readings for the same timestamp" in errors
    assert "Negative energy values detected" in errors
    assert "Voltage values outside expected synthetic range" in errors
    assert "Power factor values outside [0, 1]" in errors


def test_data_quality_summary_counts_expected_missing_and_anomalies():
    readings = pd.DataFrame(
        [
            {"quality_flag": "OK"},
            {"quality_flag": "ANOMALY"},
        ]
    )

    summary = data_quality_summary(readings, expected_readings=4)

    assert summary == {
        "expected_readings": 4,
        "received_readings": 2,
        "missing_readings": 2,
        "anomalous_readings": 1,
        "availability_percent": 50.0,
    }
