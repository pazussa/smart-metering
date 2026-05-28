# Node-RED

Node-RED is included as an optional MQTT visualization and routing component.

Basic manual flow:

1. Start services with `docker-compose up -d mosquitto nodered`.
2. Open `http://localhost:1880`.
3. Create an MQTT input subscribed to `smart-metering/readings/#`.
4. Connect it to a JSON parser and debug node.
5. Run `python -m src.mqtt_publisher --max-messages 10`.

The Python MQTT publisher and consumer are the tested protocol reference for this lab.

