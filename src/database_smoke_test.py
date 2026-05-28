from __future__ import annotations

import argparse

from sqlalchemy import create_engine, text

from src.config import SETTINGS

REQUIRED_COUNTS = {
    "feeders": 1,
    "transformers": 1,
    "meters": 1,
    "meter_readings": 1,
    "macro_readings": 1,
    "energy_balance": 1,
}


def run_database_smoke_test(database_url: str = SETTINGS.database_url) -> dict[str, int]:
    engine = create_engine(database_url, future=True)
    counts: dict[str, int] = {}
    with engine.begin() as connection:
        for table_name in REQUIRED_COUNTS:
            counts[table_name] = int(
                connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
            )
        latest_balances = int(
            connection.execute(
                text("SELECT COUNT(*) FROM v_transformer_latest_balance")
            ).scalar_one()
        )
        open_alerts = int(
            connection.execute(text("SELECT COUNT(*) FROM v_open_alerts")).scalar_one()
        )

    for table_name, minimum in REQUIRED_COUNTS.items():
        if counts[table_name] < minimum:
            raise RuntimeError(f"{table_name} has {counts[table_name]} rows; expected >= {minimum}")
    if latest_balances < 1:
        raise RuntimeError("v_transformer_latest_balance returned no rows")

    counts["v_transformer_latest_balance"] = latest_balances
    counts["v_open_alerts"] = open_alerts
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a PostgreSQL/PostGIS smoke test.")
    parser.add_argument("--database-url", default=SETTINGS.database_url)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    counts = run_database_smoke_test(args.database_url)
    for key, value in counts.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
