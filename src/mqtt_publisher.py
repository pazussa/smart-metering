from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import SETTINGS, SYNTHETIC_DIR

TOPIC_PREFIX = "smart-metering/readings"


def build_reading_payload(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    data = dict(row)
    return {
        "meter_id": str(data["meter_id"]),
        "timestamp": str(data["reading_timestamp"]),
        "energy_kwh": float(data["energy_kwh"]),
        "voltage_v": float(data["voltage_v"]),
        "current_a": float(data["current_a"]),
        "power_factor": float(data["power_factor"]),
        "quality_flag": str(data.get("quality_flag", "OK")),
    }


def publish_readings(
    delay_seconds: float = 0.05,
    max_messages: int = 500,
    mqtt_host: str = SETTINGS.mqtt_host,
    mqtt_port: int = SETTINGS.mqtt_port,
    readings_file: str | Path = SYNTHETIC_DIR / "readings.csv",
) -> int:
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("paho-mqtt is required for MQTT publishing") from exc

    readings = pd.read_csv(readings_file).head(max_messages)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

    published = 0
    try:
        for _, row in readings.iterrows():
            payload = build_reading_payload(row)
            topic = f"{TOPIC_PREFIX}/{payload['meter_id']}"
            result = client.publish(topic, json.dumps(payload), qos=0)
            result.wait_for_publish(timeout=5)
            published += 1
            print(f"Published to {topic}: {payload}")
            time.sleep(delay_seconds)
    finally:
        client.loop_stop()
        client.disconnect()

    return published


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish synthetic readings over MQTT.")
    parser.add_argument("--host", default=SETTINGS.mqtt_host)
    parser.add_argument("--port", type=int, default=SETTINGS.mqtt_port)
    parser.add_argument("--max-messages", type=int, default=500)
    parser.add_argument("--delay-seconds", type=float, default=0.05)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = publish_readings(
        delay_seconds=args.delay_seconds,
        max_messages=args.max_messages,
        mqtt_host=args.host,
        mqtt_port=args.port,
    )
    print(f"Published {count} MQTT messages.")


if __name__ == "__main__":
    main()
