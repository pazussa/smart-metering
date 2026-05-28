from __future__ import annotations

import argparse
import json
import threading
import time
from typing import Any

from src.config import SETTINGS

TOPIC = "smart-metering/smoke/test"


def run_mqtt_smoke_test(
    host: str = SETTINGS.mqtt_host,
    port: int = SETTINGS.mqtt_port,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("paho-mqtt is required for MQTT smoke testing") from exc

    received: dict[str, Any] = {}
    message_event = threading.Event()
    connect_event = threading.Event()
    connect_errors: list[str] = []

    def is_success_reason(reason_code: object) -> bool:
        value = getattr(reason_code, "value", reason_code)
        try:
            return int(value) == 0
        except (TypeError, ValueError):
            return str(reason_code).lower() in {"success", "0"}

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if is_success_reason(reason_code):
            client.subscribe(TOPIC)
        else:
            connect_errors.append(f"MQTT connection failed with reason code {reason_code}")
        connect_event.set()

    def on_message(client, userdata, message):
        received.update(json.loads(message.payload.decode("utf-8")))
        message_event.set()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            client.connect(host, port, 60)
            break
        except OSError as exc:
            last_error = exc
            time.sleep(0.5)
    else:
        raise ConnectionError(f"Could not connect to MQTT broker at {host}:{port}: {last_error}")

    client.loop_start()
    try:
        if not connect_event.wait(timeout_seconds):
            raise TimeoutError("MQTT broker did not acknowledge the connection")
        if connect_errors:
            raise RuntimeError(connect_errors[0])
        payload = {
            "meter_id": "SM-SMOKE",
            "timestamp": "2026-01-01T00:00:00",
            "energy_kwh": 1.23,
            "quality_flag": "OK",
        }
        publish = client.publish(TOPIC, json.dumps(payload), qos=1)
        publish.wait_for_publish(timeout=timeout_seconds)
        if not message_event.wait(timeout_seconds):
            raise TimeoutError("MQTT smoke message was not received")
        if received.get("meter_id") != payload["meter_id"]:
            raise RuntimeError(f"Unexpected MQTT payload: {received}")
        return received
    finally:
        client.loop_stop()
        client.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an MQTT publish/subscribe smoke test.")
    parser.add_argument("--host", default=SETTINGS.mqtt_host)
    parser.add_argument("--port", type=int, default=SETTINGS.mqtt_port)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_mqtt_smoke_test(args.host, args.port, args.timeout_seconds)
    print(f"MQTT smoke test received: {payload}")


if __name__ == "__main__":
    main()
