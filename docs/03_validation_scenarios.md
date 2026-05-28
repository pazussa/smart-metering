# Validation Scenarios

| Scenario | How to validate | Expected result |
|---|---|---|
| E01 normal operation | Generate readings with low missing probability | Availability stays high and losses remain bounded |
| E02 missing communication | Increase `--missing-probability` or run `simulate_meter_failures` | Communication events and low availability alerts appear |
| E03 anomalous reading | Increase `--anomaly-probability` | Meter alerts with `ANOMALOUS_READING` appear |
| E04 high loss sector | Lower anomaly/loss thresholds in `detect_anomalies` | Transformer alerts with `HIGH_LOSS` appear |
| E05 incomplete data | Remove readings for a window | Balance still computes with zero received readings where needed |
| E06 macro reading | Inspect `macro_readings.csv` | Every transformer has one macro row per timestamp |
| E07 transformer aggregation | Run tests for energy balance | Downstream meter readings sum by transformer and timestamp |
| E08 MQTT flow | Start Mosquitto and run publisher/consumer | JSON readings are published on `smart-metering/readings/#` |
| E09 Modbus flow | Run server then client | Four holding registers decode into electrical values |
| E10 GIS view | Run `export_geojson` and open in QGIS | Assets appear as point layers with useful properties |

