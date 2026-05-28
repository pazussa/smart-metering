import pandas as pd

from src.detect_anomalies import detect_alerts_from_frames


def test_detects_high_loss_low_availability_and_anomalous_readings():
    balance = pd.DataFrame(
        [
            {
                "transformer_id": "TR-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "loss_percent": 20.0,
                "reading_availability_percent": 80.0,
            },
            {
                "transformer_id": "TR-02",
                "reading_timestamp": "2026-01-01 00:00:00",
                "loss_percent": 5.0,
                "reading_availability_percent": 100.0,
            },
        ]
    )
    readings = pd.DataFrame(
        [
            {
                "meter_id": "SM-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": 999.0,
                "voltage_v": 120.0,
                "quality_flag": "ANOMALY",
            }
        ]
    )

    alerts = detect_alerts_from_frames(balance, readings)

    assert set(alerts["alert_type"]) == {
        "HIGH_LOSS",
        "LOW_READING_AVAILABILITY",
        "ANOMALOUS_READING",
    }
    assert (alerts["status"] == "OPEN").all()


def test_detects_voltage_range_anomaly_even_without_flag():
    balance = pd.DataFrame()
    readings = pd.DataFrame(
        [
            {
                "meter_id": "SM-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": 1.0,
                "voltage_v": 170.0,
                "quality_flag": "OK",
            }
        ]
    )

    alerts = detect_alerts_from_frames(balance, readings)

    assert len(alerts) == 1
    assert alerts.iloc[0]["alert_type"] == "ANOMALOUS_READING"
