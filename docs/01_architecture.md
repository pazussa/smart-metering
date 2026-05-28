# Architecture

The lab has four layers:

1. Synthetic simulation: Python scripts generate feeders, transformers, smart meters, macro meter readings, downstream readings and communication events.
2. Analytical processing: Python calculates transformer balances, losses, reading availability and alerts.
3. Persistence and visualization: PostgreSQL/PostGIS stores assets and indicators; Grafana reads operational panels; QGIS can read either PostGIS geometry or `maps/assets.geojson`.
4. Telemetry protocols: MQTT publishes synthetic readings; Modbus exposes a small register model; OpenDSS runs a simple feeder case.

Default local flow:

```bash
python -m src.generate_assets
python -m src.generate_synthetic_readings
python -m src.calculate_energy_balance
python -m src.detect_anomalies
python -m src.export_geojson
```

Optional service flow:

```bash
docker-compose up -d
python -m src.database_loader --reset
uvicorn src.api:app --reload
```

