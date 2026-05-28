# Data Model

Main entities:

- `feeders`: feeder metadata and point geometry.
- `transformers`: transformer metadata, feeder relation, sector and point geometry.
- `meters`: smart meters and macro meters connected to transformers.
- `meter_readings`: hourly synthetic downstream readings.
- `macro_readings`: hourly input energy by transformer.
- `communication_events`: missing readings and injected outages.
- `energy_balance`: calculated supplied energy, measured energy, losses and availability.
- `alerts`: operational alerts.

Key relationships:

- One feeder has many transformers.
- One transformer has many meters.
- Smart meters generate `meter_readings`.
- Transformers generate `macro_readings`.
- `energy_balance` joins macro readings with downstream meter sums.

Spatial fields use EPSG:4326 PostGIS points generated from latitude and longitude.

