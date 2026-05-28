import json

from src.modbus_client import decode_reading_registers
from src.modbus_server import build_server_context, encode_reading_registers
from src.mqtt_consumer import decode_payload
from src.mqtt_publisher import build_reading_payload
from src.opendss_runner import run_opendss


def test_mqtt_payload_round_trip():
    payload = build_reading_payload(
        {
            "meter_id": "SM-01",
            "reading_timestamp": "2026-01-01 00:00:00",
            "energy_kwh": "12.5",
            "voltage_v": "120.1",
            "current_a": "10.2",
            "power_factor": "0.94",
            "quality_flag": "OK",
        }
    )

    decoded = decode_payload(json.dumps(payload).encode("utf-8"))

    assert decoded["meter_id"] == "SM-01"
    assert decoded["energy_kwh"] == 12.5


def test_modbus_register_encoding_round_trip():
    registers = encode_reading_registers(
        energy_kwh=125.34,
        voltage_v=120.1,
        current_a=10.42,
        power_factor=0.94,
    )

    assert registers == [12534, 1201, 1042, 940]
    assert decode_reading_registers(registers) == {
        "energy_kwh": 125.34,
        "voltage_v": 120.1,
        "current_a": 10.42,
        "power_factor": 0.94,
    }


def test_modbus_server_context_builds_with_installed_pymodbus():
    context = build_server_context([1, 2, 3, 4])

    assert context is not None


def test_opendss_runner_can_skip_when_optional_dependency_is_missing():
    result = run_opendss(allow_missing=True)

    assert result["status"] in {"ok", "not_converged", "skipped"}
