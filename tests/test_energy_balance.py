import pandas as pd

from src.calculate_energy_balance import (
    calculate_availability,
    calculate_energy_balance_from_frames,
    calculate_loss,
)


def test_loss_calculation():
    loss_kwh, loss_percent = calculate_loss(100.0, 85.0)
    assert loss_kwh == 15.0
    assert loss_percent == 15.0


def test_zero_input_energy_does_not_divide_by_zero():
    loss_kwh, loss_percent = calculate_loss(0.0, 5.0)
    assert loss_kwh == -5.0
    assert loss_percent == 0.0


def test_availability_calculation():
    assert calculate_availability(10, 9) == 90.0
    assert calculate_availability(0, 0) == 0.0


def test_energy_balance_aggregates_by_transformer_and_timestamp():
    meters = pd.DataFrame(
        [
            {"meter_id": "MM-01", "transformer_id": "TR-01", "is_macro": True},
            {"meter_id": "SM-01", "transformer_id": "TR-01", "is_macro": False},
            {"meter_id": "SM-02", "transformer_id": "TR-01", "is_macro": False},
        ]
    )
    readings = pd.DataFrame(
        [
            {
                "meter_id": "SM-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": 40.0,
            },
            {
                "meter_id": "SM-02",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": 45.0,
            },
        ]
    )
    macro = pd.DataFrame(
        [
            {
                "transformer_id": "TR-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "input_energy_kwh": 100.0,
            }
        ]
    )

    balance = calculate_energy_balance_from_frames(meters, readings, macro)

    row = balance.iloc[0]
    assert row["measured_energy_kwh"] == 85.0
    assert row["loss_kwh"] == 15.0
    assert row["loss_percent"] == 15.0
    assert row["expected_readings"] == 2
    assert row["received_readings"] == 2
    assert row["reading_availability_percent"] == 100.0


def test_energy_balance_handles_missing_downstream_readings():
    meters = pd.DataFrame(
        [
            {"meter_id": "MM-01", "transformer_id": "TR-01", "is_macro": True},
            {"meter_id": "SM-01", "transformer_id": "TR-01", "is_macro": False},
            {"meter_id": "SM-02", "transformer_id": "TR-01", "is_macro": False},
        ]
    )
    readings = pd.DataFrame(
        [
            {
                "meter_id": "SM-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "energy_kwh": 30.0,
            }
        ]
    )
    macro = pd.DataFrame(
        [
            {
                "transformer_id": "TR-01",
                "reading_timestamp": "2026-01-01 00:00:00",
                "input_energy_kwh": 100.0,
            }
        ]
    )

    balance = calculate_energy_balance_from_frames(meters, readings, macro)

    row = balance.iloc[0]
    assert row["measured_energy_kwh"] == 30.0
    assert row["received_readings"] == 1
    assert row["expected_readings"] == 2
    assert row["reading_availability_percent"] == 50.0
