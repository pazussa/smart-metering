from __future__ import annotations

import argparse
import json

from src.config import SETTINGS

TOPIC = "smart-metering/readings/#"


def decode_payload(raw_payload: bytes) -> dict[str, object]:
    return json.loads(raw_payload.decode("utf-8"))


def run_consumer(
    mqtt_host: str = SETTINGS.mqtt_host,
    mqtt_port: int = SETTINGS.mqtt_port,
    topic: str = TOPIC,
) -> None:
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("paho-mqtt is required for MQTT consuming") from exc

    def on_connect(client, userdata, flags, reason_code, properties=None):
        print(f"Connected with reason code: {reason_code}")
        client.subscribe(topic)

    def on_message(client, userdata, message):
        print(f"Topic: {message.topic}")
        print(decode_payload(message.payload))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consume synthetic readings from MQTT.")
    parser.add_argument("--host", default=SETTINGS.mqtt_host)
    parser.add_argument("--port", type=int, default=SETTINGS.mqtt_port)
    parser.add_argument("--topic", default=TOPIC)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_consumer(args.host, args.port, args.topic)


if __name__ == "__main__":
    main()
