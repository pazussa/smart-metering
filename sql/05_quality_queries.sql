CREATE OR REPLACE VIEW v_data_quality_by_transformer AS
SELECT
    eb.transformer_id,
    t.sector,
    AVG(eb.reading_availability_percent) AS avg_availability_percent,
    SUM(eb.expected_readings - eb.received_readings) AS missing_readings,
    AVG(eb.loss_percent) AS avg_loss_percent
FROM energy_balance eb
JOIN transformers t ON t.transformer_id = eb.transformer_id
GROUP BY eb.transformer_id, t.sector;

CREATE OR REPLACE VIEW v_meter_anomaly_counts AS
SELECT
    meter_id,
    COUNT(*) FILTER (WHERE quality_flag = 'ANOMALY') AS anomalous_readings,
    COUNT(*) AS total_readings
FROM meter_readings
GROUP BY meter_id;

