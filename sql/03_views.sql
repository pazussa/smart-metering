CREATE OR REPLACE VIEW v_transformer_latest_balance AS
SELECT DISTINCT ON (eb.transformer_id)
    eb.transformer_id,
    t.name AS transformer_name,
    t.sector,
    eb.reading_timestamp,
    eb.input_energy_kwh,
    eb.measured_energy_kwh,
    eb.loss_kwh,
    eb.loss_percent,
    eb.reading_availability_percent
FROM energy_balance eb
JOIN transformers t ON t.transformer_id = eb.transformer_id
ORDER BY eb.transformer_id, eb.reading_timestamp DESC;

CREATE OR REPLACE VIEW v_open_alerts AS
SELECT
    alert_id,
    entity_type,
    entity_id,
    alert_timestamp,
    alert_type,
    alert_message,
    severity,
    status
FROM alerts
WHERE status = 'OPEN'
ORDER BY alert_timestamp DESC;

CREATE OR REPLACE VIEW v_transformer_loss_summary AS
SELECT
    eb.transformer_id,
    t.name AS transformer_name,
    t.sector,
    AVG(eb.loss_percent) AS avg_loss_percent,
    MAX(eb.loss_percent) AS max_loss_percent,
    AVG(eb.reading_availability_percent) AS avg_availability_percent,
    COUNT(*) AS balance_points
FROM energy_balance eb
JOIN transformers t ON t.transformer_id = eb.transformer_id
GROUP BY eb.transformer_id, t.name, t.sector;

