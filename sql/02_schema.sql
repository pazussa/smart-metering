CREATE TABLE IF NOT EXISTS feeders (
    feeder_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    voltage_kv NUMERIC(8,3),
    zone TEXT,
    geom GEOMETRY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS transformers (
    transformer_id TEXT PRIMARY KEY,
    feeder_id TEXT NOT NULL REFERENCES feeders(feeder_id),
    name TEXT NOT NULL,
    capacity_kva NUMERIC(10,2),
    sector TEXT,
    geom GEOMETRY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS meters (
    meter_id TEXT PRIMARY KEY,
    transformer_id TEXT NOT NULL REFERENCES transformers(transformer_id),
    customer_type TEXT NOT NULL,
    is_macro BOOLEAN DEFAULT FALSE,
    communication_type TEXT,
    installation_status TEXT DEFAULT 'ACTIVE',
    geom GEOMETRY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS meter_readings (
    reading_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meter_id TEXT NOT NULL REFERENCES meters(meter_id),
    reading_timestamp TIMESTAMP NOT NULL,
    energy_kwh NUMERIC(14,4) NOT NULL CHECK (energy_kwh >= 0),
    voltage_v NUMERIC(10,2),
    current_a NUMERIC(10,2),
    power_factor NUMERIC(5,3),
    quality_flag TEXT DEFAULT 'OK',
    source TEXT DEFAULT 'synthetic',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (meter_id, reading_timestamp)
);

CREATE TABLE IF NOT EXISTS macro_readings (
    reading_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transformer_id TEXT NOT NULL REFERENCES transformers(transformer_id),
    reading_timestamp TIMESTAMP NOT NULL,
    input_energy_kwh NUMERIC(14,4) NOT NULL CHECK (input_energy_kwh >= 0),
    quality_flag TEXT DEFAULT 'OK',
    source TEXT DEFAULT 'synthetic',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (transformer_id, reading_timestamp)
);

CREATE TABLE IF NOT EXISTS communication_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meter_id TEXT NOT NULL REFERENCES meters(meter_id),
    event_timestamp TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL,
    event_description TEXT,
    severity TEXT DEFAULT 'LOW',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS energy_balance (
    balance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transformer_id TEXT NOT NULL REFERENCES transformers(transformer_id),
    reading_timestamp TIMESTAMP NOT NULL,
    input_energy_kwh NUMERIC(14,4) NOT NULL,
    measured_energy_kwh NUMERIC(14,4) NOT NULL,
    loss_kwh NUMERIC(14,4) NOT NULL,
    loss_percent NUMERIC(8,4) NOT NULL,
    expected_readings INT,
    received_readings INT,
    reading_availability_percent NUMERIC(8,4),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (transformer_id, reading_timestamp)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    alert_timestamp TIMESTAMP NOT NULL,
    alert_type TEXT NOT NULL,
    alert_message TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transformers_geom ON transformers USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_meters_geom ON meters USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_meter_readings_ts ON meter_readings (reading_timestamp);
CREATE INDEX IF NOT EXISTS idx_macro_readings_ts ON macro_readings (reading_timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_balance_ts ON energy_balance (reading_timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status);

