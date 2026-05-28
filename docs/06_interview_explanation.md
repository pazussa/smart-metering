# Interview Explanation

This project is a reproducible smart-metering lab for macro-metering, telemetry and energy-loss analysis.

It simulates a distribution network with feeders, transformers, macro meters and downstream smart meters. Python generates realistic hourly readings, communication gaps and anomalous measurements. The processing layer calculates transformer-level energy balance, kWh losses, loss percentage and telemetry availability. It also creates operational alerts for high losses, missing readings and anomalous data.

The data can be loaded into PostgreSQL/PostGIS for SQL analysis, Grafana dashboards and QGIS maps. MQTT and Modbus scripts demonstrate telemetry concepts, while OpenDSS provides a simple distribution feeder simulation.

The important point is that the project is not connected to real utility infrastructure. It is a controlled, reproducible case study that demonstrates data engineering, metering concepts, communications and operational analytics for electric distribution.

