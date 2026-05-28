# Indicators

| Indicator | Formula |
|---|---|
| Supplied energy | `macro_readings.input_energy_kwh` |
| Measured energy | Sum of `meter_readings.energy_kwh` by transformer and timestamp |
| Loss kWh | `input_energy_kwh - measured_energy_kwh` |
| Loss percent | `loss_kwh / input_energy_kwh * 100` |
| Reading availability | `received_readings / expected_readings * 100` |
| Missing readings | `expected_readings - received_readings` |
| Critical transformer | `loss_percent > threshold` |
| Low telemetry availability | `reading_availability_percent < threshold` |
| Anomalous reading | Synthetic `quality_flag = ANOMALY` or voltage outside configured range |

The default thresholds are 12 percent for high loss and 95 percent for low availability.

