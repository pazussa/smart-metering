from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import PROCESSED_DIR, SETTINGS, SQL_DIR, SYNTHETIC_DIR, ensure_project_dirs
from src.generate_synthetic_readings import coerce_bool


def get_engine(database_url: str = SETTINGS.database_url) -> Engine:
    return create_engine(database_url, future=True)


def execute_sql_files(engine: Engine, sql_files: Iterable[Path] | None = None) -> None:
    files = list(sql_files or sorted(SQL_DIR.glob("*.sql")))
    with engine.begin() as connection:
        for sql_file in files:
            sql = sql_file.read_text(encoding="utf-8")
            if sql.strip():
                connection.execute(text(sql))


def reset_lab_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("""
                TRUNCATE TABLE
                    alerts,
                    energy_balance,
                    communication_events,
                    macro_readings,
                    meter_readings,
                    meters,
                    transformers,
                    feeders
                RESTART IDENTITY CASCADE
                """))


def _records(frame: pd.DataFrame) -> list[dict[str, object]]:
    clean = frame.where(pd.notna(frame), None)
    return clean.to_dict(orient="records")


def load_assets(engine: Engine, synthetic_dir: str | Path = SYNTHETIC_DIR) -> None:
    synthetic_path = Path(synthetic_dir)
    feeders = pd.read_csv(synthetic_path / "feeders.csv")
    transformers = pd.read_csv(synthetic_path / "transformers.csv")
    meters = pd.read_csv(synthetic_path / "meters.csv")
    meters["is_macro"] = coerce_bool(meters["is_macro"])

    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO feeders (feeder_id, name, voltage_kv, zone, geom)
                VALUES (:feeder_id, :name, :voltage_kv, :zone,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                ON CONFLICT (feeder_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    voltage_kv = EXCLUDED.voltage_kv,
                    zone = EXCLUDED.zone,
                    geom = EXCLUDED.geom
                """),
            _records(feeders),
        )
        connection.execute(
            text("""
                INSERT INTO transformers
                    (transformer_id, feeder_id, name, capacity_kva, sector, geom)
                VALUES (:transformer_id, :feeder_id, :name, :capacity_kva, :sector,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                ON CONFLICT (transformer_id) DO UPDATE SET
                    feeder_id = EXCLUDED.feeder_id,
                    name = EXCLUDED.name,
                    capacity_kva = EXCLUDED.capacity_kva,
                    sector = EXCLUDED.sector,
                    geom = EXCLUDED.geom
                """),
            _records(transformers),
        )
        connection.execute(
            text("""
                INSERT INTO meters
                    (meter_id, transformer_id, customer_type, is_macro,
                     communication_type, installation_status, geom)
                VALUES (:meter_id, :transformer_id, :customer_type, :is_macro,
                        :communication_type, :installation_status,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                ON CONFLICT (meter_id) DO UPDATE SET
                    transformer_id = EXCLUDED.transformer_id,
                    customer_type = EXCLUDED.customer_type,
                    is_macro = EXCLUDED.is_macro,
                    communication_type = EXCLUDED.communication_type,
                    installation_status = EXCLUDED.installation_status,
                    geom = EXCLUDED.geom
                """),
            _records(meters),
        )


def load_readings(engine: Engine, synthetic_dir: str | Path = SYNTHETIC_DIR) -> None:
    synthetic_path = Path(synthetic_dir)
    readings = pd.read_csv(synthetic_path / "readings.csv", parse_dates=["reading_timestamp"])
    macro = pd.read_csv(synthetic_path / "macro_readings.csv", parse_dates=["reading_timestamp"])
    events_file = synthetic_path / "communication_events.csv"
    events = (
        pd.read_csv(events_file, parse_dates=["event_timestamp"])
        if events_file.exists()
        else pd.DataFrame()
    )

    with engine.begin() as connection:
        if not readings.empty:
            connection.execute(
                text("""
                    INSERT INTO meter_readings
                        (meter_id, reading_timestamp, energy_kwh, voltage_v, current_a,
                         power_factor, quality_flag, source)
                    VALUES (:meter_id, :reading_timestamp, :energy_kwh, :voltage_v,
                            :current_a, :power_factor, :quality_flag, :source)
                    ON CONFLICT (meter_id, reading_timestamp) DO UPDATE SET
                        energy_kwh = EXCLUDED.energy_kwh,
                        voltage_v = EXCLUDED.voltage_v,
                        current_a = EXCLUDED.current_a,
                        power_factor = EXCLUDED.power_factor,
                        quality_flag = EXCLUDED.quality_flag,
                        source = EXCLUDED.source
                    """),
                _records(readings),
            )
        if not macro.empty:
            connection.execute(
                text("""
                    INSERT INTO macro_readings
                        (transformer_id, reading_timestamp, input_energy_kwh,
                         quality_flag, source)
                    VALUES (:transformer_id, :reading_timestamp, :input_energy_kwh,
                            :quality_flag, :source)
                    ON CONFLICT (transformer_id, reading_timestamp) DO UPDATE SET
                        input_energy_kwh = EXCLUDED.input_energy_kwh,
                        quality_flag = EXCLUDED.quality_flag,
                        source = EXCLUDED.source
                    """),
                _records(macro),
            )
        if not events.empty:
            connection.execute(text("DELETE FROM communication_events"))
            connection.execute(
                text("""
                    INSERT INTO communication_events
                        (meter_id, event_timestamp, event_type, event_description, severity)
                    VALUES (:meter_id, :event_timestamp, :event_type,
                            :event_description, :severity)
                    """),
                _records(events),
            )


def load_outputs(
    engine: Engine,
    processed_dir: str | Path = PROCESSED_DIR,
) -> None:
    processed_path = Path(processed_dir)
    balance_file = processed_path / "energy_balance.csv"
    alerts_file = processed_path / "alerts.csv"
    balance = pd.read_csv(balance_file, parse_dates=["reading_timestamp"])
    alerts = (
        pd.read_csv(alerts_file, parse_dates=["alert_timestamp"])
        if alerts_file.exists()
        else pd.DataFrame()
    )

    with engine.begin() as connection:
        if not balance.empty:
            connection.execute(
                text("""
                    INSERT INTO energy_balance
                        (transformer_id, reading_timestamp, input_energy_kwh,
                         measured_energy_kwh, loss_kwh, loss_percent,
                         expected_readings, received_readings,
                         reading_availability_percent)
                    VALUES (:transformer_id, :reading_timestamp, :input_energy_kwh,
                            :measured_energy_kwh, :loss_kwh, :loss_percent,
                            :expected_readings, :received_readings,
                            :reading_availability_percent)
                    ON CONFLICT (transformer_id, reading_timestamp) DO UPDATE SET
                        input_energy_kwh = EXCLUDED.input_energy_kwh,
                        measured_energy_kwh = EXCLUDED.measured_energy_kwh,
                        loss_kwh = EXCLUDED.loss_kwh,
                        loss_percent = EXCLUDED.loss_percent,
                        expected_readings = EXCLUDED.expected_readings,
                        received_readings = EXCLUDED.received_readings,
                        reading_availability_percent = EXCLUDED.reading_availability_percent
                    """),
                _records(balance),
            )
        connection.execute(text("DELETE FROM alerts"))
        if not alerts.empty:
            connection.execute(
                text("""
                    INSERT INTO alerts
                        (entity_type, entity_id, alert_timestamp, alert_type,
                         alert_message, severity, status)
                    VALUES (:entity_type, :entity_id, :alert_timestamp, :alert_type,
                            :alert_message, :severity, :status)
                    """),
                _records(alerts),
            )


def load_all(
    database_url: str = SETTINGS.database_url,
    reset: bool = False,
    synthetic_dir: str | Path = SYNTHETIC_DIR,
    processed_dir: str | Path = PROCESSED_DIR,
) -> None:
    ensure_project_dirs()
    engine = get_engine(database_url)
    execute_sql_files(engine)
    if reset:
        reset_lab_tables(engine)
    load_assets(engine, synthetic_dir)
    load_readings(engine, synthetic_dir)
    load_outputs(engine, processed_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load synthetic lab data into PostgreSQL/PostGIS.")
    parser.add_argument("--database-url", default=SETTINGS.database_url)
    parser.add_argument("--reset", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_all(database_url=args.database_url, reset=args.reset)
    print("Database load completed.")


if __name__ == "__main__":
    main()
