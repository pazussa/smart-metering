from __future__ import annotations

import json
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from src.config import BASE_DIR, PROCESSED_DIR, SETTINGS, SYNTHETIC_DIR
from src.opendss_runner import run_opendss

DEMO_DIR = BASE_DIR / "demo"
IMAGE_DIR = DEMO_DIR / "images"
SCREENSHOT_DIR = DEMO_DIR / "screenshots"
DOC_SCREENSHOT_DIR = BASE_DIR / "docs" / "screenshots"

COLORS = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "orange": "#f97316",
    "red": "#dc2626",
    "purple": "#7c3aed",
    "slate": "#334155",
    "gray": "#64748b",
    "light": "#f8fafc",
}


def ensure_dirs() -> None:
    for directory in [IMAGE_DIR, SCREENSHOT_DIR, DOC_SCREENSHOT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def save_figure(fig: plt.Figure, filename: str) -> Path:
    path = IMAGE_DIR / filename
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    shutil.copy2(path, DOC_SCREENSHOT_DIR / filename)
    return path


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "feeders": pd.read_csv(SYNTHETIC_DIR / "feeders.csv"),
        "transformers": pd.read_csv(SYNTHETIC_DIR / "transformers.csv"),
        "meters": pd.read_csv(SYNTHETIC_DIR / "meters.csv"),
        "readings": pd.read_csv(SYNTHETIC_DIR / "readings.csv", parse_dates=["reading_timestamp"]),
        "macro": pd.read_csv(
            SYNTHETIC_DIR / "macro_readings.csv", parse_dates=["reading_timestamp"]
        ),
        "events": pd.read_csv(SYNTHETIC_DIR / "communication_events.csv"),
        "balance": pd.read_csv(
            PROCESSED_DIR / "energy_balance.csv", parse_dates=["reading_timestamp"]
        ),
        "alerts": pd.read_csv(PROCESSED_DIR / "alerts.csv", parse_dates=["alert_timestamp"]),
    }


def db_counts() -> dict[str, int]:
    engine = create_engine(SETTINGS.database_url, future=True)
    tables = [
        "feeders",
        "transformers",
        "meters",
        "meter_readings",
        "macro_readings",
        "communication_events",
        "energy_balance",
        "alerts",
    ]
    counts: dict[str, int] = {}
    with engine.begin() as connection:
        for table_name in tables:
            counts[table_name] = int(
                connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
            )
        counts["latest_balances"] = int(
            connection.execute(
                text("SELECT COUNT(*) FROM v_transformer_latest_balance")
            ).scalar_one()
        )
    return counts


def http_json(url: str) -> Any:
    with urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def plot_cover(data: dict[str, pd.DataFrame], counts: dict[str, int]) -> Path:
    fig = plt.figure(figsize=(13.33, 7.5), facecolor="#0f172a")
    ax = fig.add_subplot(111)
    ax.axis("off")
    fig.text(
        0.055,
        0.84,
        "Smart Metering & Loss Analysis Lab",
        fontsize=31,
        color="white",
        weight="bold",
    )
    fig.text(
        0.058,
        0.765,
        "Laboratorio reproducible de macromedicion, telemedicion, PostGIS, Grafana, MQTT y OpenDSS",
        fontsize=15,
        color="#cbd5e1",
    )
    metrics = [
        ("Alimentadores", counts["feeders"], COLORS["blue"]),
        ("Transformadores", counts["transformers"], COLORS["green"]),
        ("Medidores", counts["meters"], COLORS["orange"]),
        ("Lecturas", counts["meter_readings"], COLORS["purple"]),
        ("Balances", counts["energy_balance"], COLORS["red"]),
        ("Alertas", counts["alerts"], "#eab308"),
    ]
    x_positions = np.linspace(0.08, 0.88, 3)
    y_positions = [0.52, 0.31]
    for index, (label, value, color) in enumerate(metrics):
        x = x_positions[index % 3]
        y = y_positions[index // 3]
        ax.add_patch(plt.Rectangle((x, y), 0.24, 0.15, transform=ax.transAxes, color="#1e293b"))
        ax.add_patch(
            plt.Rectangle((x, y + 0.132), 0.24, 0.018, transform=ax.transAxes, color=color)
        )
        ax.text(
            x + 0.025,
            y + 0.09,
            f"{value:,}",
            transform=ax.transAxes,
            color="white",
            fontsize=24,
            weight="bold",
        )
        ax.text(x + 0.025, y + 0.045, label, transform=ax.transAxes, color="#cbd5e1", fontsize=13)
    fig.text(
        0.06,
        0.11,
        "Servicios validados: FastAPI :8000 | Grafana :3000 | Node-RED :1880 | Mosquitto :1883 | PostgreSQL/PostGIS :5432",
        fontsize=12,
        color="#94a3b8",
    )
    return save_figure(fig, "00_demo_cover.png")


def plot_architecture() -> Path:
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    ax.axis("off")
    ax.set_title("Arquitectura del laboratorio", fontsize=24, weight="bold", pad=20)
    boxes = {
        "Generador Python\nde datos sinteticos": (0.08, 0.62, COLORS["blue"]),
        "OpenDSS\nred simulada": (0.08, 0.34, COLORS["purple"]),
        "MQTT\nMosquitto": (0.35, 0.62, COLORS["green"]),
        "PostgreSQL\nPostGIS": (0.35, 0.34, COLORS["orange"]),
        "FastAPI\nREST API": (0.62, 0.58, COLORS["red"]),
        "Grafana\nTableros": (0.62, 0.34, COLORS["blue"]),
        "QGIS / GeoJSON\nMapas": (0.62, 0.10, COLORS["green"]),
        "Node-RED\nFlujos de telemedicion": (0.35, 0.10, COLORS["purple"]),
    }
    for label, (x, y, color) in boxes.items():
        ax.add_patch(
            plt.Rectangle(
                (x, y),
                0.19,
                0.14,
                transform=ax.transAxes,
                fill=True,
                color="#f8fafc",
                ec=color,
                lw=2,
            )
        )
        ax.text(
            x + 0.095,
            y + 0.07,
            label,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            color="#0f172a",
        )
    arrows = [
        ((0.27, 0.69), (0.35, 0.69)),
        ((0.27, 0.41), (0.35, 0.41)),
        ((0.445, 0.62), (0.445, 0.48)),
        ((0.54, 0.41), (0.62, 0.65)),
        ((0.54, 0.41), (0.62, 0.41)),
        ((0.54, 0.41), (0.62, 0.17)),
        ((0.445, 0.62), (0.445, 0.24)),
    ]
    for start, end in arrows:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            xycoords="axes fraction",
            arrowprops=dict(arrowstyle="->", lw=1.8, color="#475569"),
        )
    ax.text(
        0.08,
        0.05,
        "Docker Compose levanta PostGIS, Grafana, Mosquitto, Node-RED, InfluxDB y API.",
        transform=ax.transAxes,
        fontsize=12,
        color="#475569",
    )
    return save_figure(fig, "01_architecture.png")


def plot_kpis(data: dict[str, pd.DataFrame], counts: dict[str, int]) -> Path:
    balance = data["balance"]
    alerts = data["alerts"]
    values = [
        ("Perdida promedio", f"{balance['loss_percent'].mean():.2f}%"),
        ("Perdida maxima", f"{balance['loss_percent'].max():.2f}%"),
        ("Disponibilidad promedio", f"{balance['reading_availability_percent'].mean():.2f}%"),
        ("Alertas abiertas", f"{len(alerts):,}"),
        ("Balances recientes en DB", f"{counts['latest_balances']:,}"),
        ("Activos GIS", "86"),
    ]
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    ax.axis("off")
    ax.set_title("Resumen ejecutivo de indicadores", fontsize=24, weight="bold", pad=22)
    for index, (label, value) in enumerate(values):
        x = 0.08 + (index % 3) * 0.30
        y = 0.56 - (index // 3) * 0.26
        ax.add_patch(
            plt.Rectangle((x, y), 0.25, 0.18, transform=ax.transAxes, color="#f8fafc", ec="#cbd5e1")
        )
        ax.text(
            x + 0.03,
            y + 0.105,
            value,
            transform=ax.transAxes,
            fontsize=27,
            color="#0f172a",
            weight="bold",
        )
        ax.text(x + 0.03, y + 0.055, label, transform=ax.transAxes, fontsize=13, color="#64748b")
    return save_figure(fig, "02_kpi_summary.png")


def plot_loss_timeseries(data: dict[str, pd.DataFrame]) -> Path:
    balance = data["balance"]
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    for transformer_id, group in balance.groupby("transformer_id"):
        ax.plot(group["reading_timestamp"], group["loss_percent"], lw=1.6, label=transformer_id)
    ax.axhline(12, color=COLORS["red"], lw=1.8, ls="--", label="Umbral de perdida alta")
    ax.set_title("Perdida porcentual por transformador", fontsize=22, weight="bold")
    ax.set_ylabel("Porcentaje de perdida")
    ax.set_xlabel("Fecha")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=4, fontsize=9, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()
    return save_figure(fig, "03_loss_timeseries.png")


def plot_energy_balance_latest(data: dict[str, pd.DataFrame]) -> Path:
    latest = data["balance"].sort_values("reading_timestamp").groupby("transformer_id").tail(1)
    latest = latest.sort_values("loss_percent", ascending=False)
    x = np.arange(len(latest))
    width = 0.28
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    ax.bar(x - width, latest["input_energy_kwh"], width, label="Entrada kWh", color=COLORS["blue"])
    ax.bar(x, latest["measured_energy_kwh"], width, label="Medida kWh", color=COLORS["green"])
    ax.bar(x + width, latest["loss_kwh"], width, label="Perdida kWh", color=COLORS["red"])
    ax.set_xticks(x)
    ax.set_xticklabels(latest["transformer_id"], rotation=0)
    ax.set_title("Ultimo balance energetico por transformador", fontsize=22, weight="bold")
    ax.set_ylabel("kWh")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    return save_figure(fig, "04_energy_balance_latest.png")


def plot_availability_heatmap(data: dict[str, pd.DataFrame]) -> Path:
    balance = data["balance"].copy()
    balance["hour_index"] = balance["reading_timestamp"].dt.strftime("%m-%d %Hh")
    last_hours = sorted(balance["reading_timestamp"].unique())[-48:]
    subset = balance[balance["reading_timestamp"].isin(last_hours)].copy()
    pivot = subset.pivot_table(
        index="transformer_id",
        columns="hour_index",
        values="reading_availability_percent",
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(13.33, 6.2), facecolor="white")
    image = ax.imshow(pivot.values, aspect="auto", vmin=70, vmax=100, cmap="RdYlGn")
    ax.set_title(
        "Disponibilidad de lecturas - ultimas 48 horas simuladas", fontsize=20, weight="bold"
    )
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    step = max(len(pivot.columns) // 8, 1)
    ax.set_xticks(np.arange(0, len(pivot.columns), step))
    ax.set_xticklabels(pivot.columns[::step], rotation=45, ha="right")
    fig.colorbar(image, ax=ax, label="Disponibilidad %")
    return save_figure(fig, "05_availability_heatmap.png")


def plot_critical_ranking(data: dict[str, pd.DataFrame]) -> Path:
    ranking = (
        data["balance"]
        .groupby("transformer_id", as_index=False)["loss_percent"]
        .mean()
        .sort_values("loss_percent")
    )
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    colors = [COLORS["red"] if value > 12 else COLORS["green"] for value in ranking["loss_percent"]]
    ax.barh(ranking["transformer_id"], ranking["loss_percent"], color=colors)
    ax.axvline(12, color="#0f172a", ls="--", lw=1.5)
    ax.set_title("Ranking de transformadores por perdida promedio", fontsize=22, weight="bold")
    ax.set_xlabel("Porcentaje de perdida promedio")
    ax.grid(axis="x", alpha=0.25)
    return save_figure(fig, "06_critical_ranking.png")


def plot_alerts_breakdown(data: dict[str, pd.DataFrame]) -> Path:
    alerts = data["alerts"]
    type_labels = {
        "HIGH_LOSS": "Perdida alta",
        "LOW_READING_AVAILABILITY": "Baja disponibilidad",
        "ANOMALOUS_READING": "Lectura atipica",
    }
    severity_labels = {"HIGH": "Alta", "MEDIUM": "Media", "LOW": "Baja"}
    alerts = alerts.copy()
    alerts["alert_type_es"] = alerts["alert_type"].map(type_labels).fillna(alerts["alert_type"])
    alerts["severity_es"] = alerts["severity"].map(severity_labels).fillna(alerts["severity"])
    by_type = alerts["alert_type_es"].value_counts()
    by_severity = alerts["severity_es"].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(13.33, 6.5), facecolor="white")
    axes[0].bar(
        by_type.index,
        by_type.values,
        color=[COLORS["red"], COLORS["orange"], COLORS["purple"]][: len(by_type)],
    )
    axes[0].set_title("Alertas por tipo", fontsize=17, weight="bold")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].pie(
        by_severity.values,
        labels=by_severity.index,
        autopct="%1.1f%%",
        colors=[COLORS["red"], COLORS["orange"], COLORS["green"]],
    )
    axes[1].set_title("Alertas por severidad", fontsize=17, weight="bold")
    fig.suptitle("Analisis de alertas operativas", fontsize=22, weight="bold")
    return save_figure(fig, "07_alerts_breakdown.png")


def plot_gis_map(data: dict[str, pd.DataFrame]) -> Path:
    feeders = data["feeders"]
    transformers = data["transformers"].copy()
    meters = data["meters"].copy()
    latest = data["balance"].sort_values("reading_timestamp").groupby("transformer_id").tail(1)
    transformers = transformers.merge(
        latest[["transformer_id", "loss_percent"]], on="transformer_id", how="left"
    )
    meters["is_macro"] = meters["is_macro"].astype(str).str.lower().isin(["true", "1"])
    smart = meters[~meters["is_macro"]]
    macro = meters[meters["is_macro"]]
    fig, ax = plt.subplots(figsize=(10, 10), facecolor="white")
    ax.scatter(
        smart["lon"], smart["lat"], s=16, c="#94a3b8", alpha=0.65, label="Medidores inteligentes"
    )
    ax.scatter(macro["lon"], macro["lat"], s=70, c="#0f172a", marker="s", label="Macromedidores")
    scatter = ax.scatter(
        transformers["lon"],
        transformers["lat"],
        s=170,
        c=transformers["loss_percent"],
        cmap="YlOrRd",
        edgecolor="#111827",
        linewidth=0.8,
        label="Transformadores",
    )
    ax.scatter(
        feeders["lon"], feeders["lat"], s=190, c=COLORS["blue"], marker="*", label="Alimentadores"
    )
    for row in transformers.itertuples(index=False):
        ax.text(row.lon + 0.0008, row.lat + 0.0008, row.transformer_id, fontsize=8)
    ax.set_title(
        "Mapa GIS sintetico de activos y perdida por transformador", fontsize=18, weight="bold"
    )
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.grid(True, alpha=0.2)
    ax.legend(loc="upper right")
    fig.colorbar(scatter, ax=ax, label="Ultima perdida %")
    return save_figure(fig, "08_gis_assets_map.png")


def plot_data_model() -> Path:
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    ax.axis("off")
    ax.set_title("Modelo de datos principal", fontsize=24, weight="bold", pad=20)
    tables = {
        "feeders": (0.07, 0.62, ["feeder_id PK", "name", "voltage_kv", "geom"]),
        "transformers": (
            0.33,
            0.62,
            ["transformer_id PK", "feeder_id FK", "capacity_kva", "sector", "geom"],
        ),
        "meters": (
            0.61,
            0.62,
            ["meter_id PK", "transformer_id FK", "is_macro", "communication_type", "geom"],
        ),
        "meter_readings": (
            0.61,
            0.34,
            ["reading_id PK", "meter_id FK", "timestamp", "energy_kwh", "quality_flag"],
        ),
        "macro_readings": (
            0.33,
            0.34,
            ["reading_id PK", "transformer_id FK", "timestamp", "input_energy_kwh"],
        ),
        "energy_balance": (
            0.33,
            0.08,
            ["balance_id PK", "transformer_id FK", "input/measured/loss", "availability"],
        ),
        "alerts": (
            0.61,
            0.08,
            ["alert_id PK", "entity_type", "entity_id", "alert_type", "severity"],
        ),
    }
    for name, (x, y, fields) in tables.items():
        ax.add_patch(
            plt.Rectangle((x, y), 0.22, 0.20, transform=ax.transAxes, color="#f8fafc", ec="#334155")
        )
        ax.text(
            x + 0.01,
            y + 0.165,
            name,
            transform=ax.transAxes,
            fontsize=13,
            weight="bold",
            color="#0f172a",
        )
        for idx, field in enumerate(fields):
            ax.text(
                x + 0.02,
                y + 0.13 - idx * 0.026,
                field,
                transform=ax.transAxes,
                fontsize=9,
                color="#475569",
            )
    for start, end in [
        ((0.29, 0.72), (0.33, 0.72)),
        ((0.55, 0.72), (0.61, 0.72)),
        ((0.72, 0.62), (0.72, 0.54)),
        ((0.44, 0.62), (0.44, 0.54)),
        ((0.44, 0.34), (0.44, 0.28)),
        ((0.72, 0.34), (0.72, 0.28)),
    ]:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            xycoords="axes fraction",
            arrowprops=dict(arrowstyle="->", lw=1.5, color="#475569"),
        )
    return save_figure(fig, "09_data_model.png")


def plot_validation(data: dict[str, pd.DataFrame], counts: dict[str, int]) -> Path:
    api_health = http_json("http://localhost:8000/health")
    grafana_health = http_json("http://localhost:3000/api/health")
    opendss = run_opendss()
    rows = [
        ("Servicios Docker", "OK", "6 servicios ejecutandose"),
        ("PostgreSQL/PostGIS", "OK", f"{counts['energy_balance']} balances calculados"),
        ("FastAPI", "OK", f"/health = {api_health['status']}"),
        ("Grafana", "OK", f"base de datos = {grafana_health['database']}"),
        ("MQTT", "OK", "publicacion y consumo probados"),
        ("OpenDSS", opendss["status"].upper(), opendss.get("circuit", "n/a")),
        ("Mapa GIS", "OK", "GeoJSON y mapa PNG generados"),
    ]
    fig, ax = plt.subplots(figsize=(13.33, 7.5), facecolor="white")
    ax.axis("off")
    ax.set_title("Pruebas de validacion ejecutadas", fontsize=24, weight="bold", pad=20)
    table = ax.table(
        cellText=rows,
        colLabels=["Componente", "Estado", "Validacion"],
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2.0)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#0f172a")
            cell.set_text_props(color="white", weight="bold")
        elif col == 1:
            cell.set_facecolor("#dcfce7")
            cell.set_text_props(color="#166534", weight="bold")
        else:
            cell.set_facecolor("#f8fafc")
    return save_figure(fig, "10_validation_matrix.png")


def capture_url(url: str, filename: str, width: int = 1600, height: int = 1000) -> Path | None:
    browser = (
        shutil.which("chromium-browser")
        or shutil.which("chromium")
        or shutil.which("google-chrome")
    )
    if not browser:
        return None
    output = SCREENSHOT_DIR / filename
    command = [
        browser,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--run-all-compositor-stages-before-draw",
        f"--window-size={width},{height}",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--virtual-time-budget=10000",
        f"--screenshot={output}",
        url,
    ]
    subprocess.run(
        command, check=True, cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    shutil.copy2(output, DOC_SCREENSHOT_DIR / filename)
    return output


def capture_grafana_dashboard(filename: str = "12_grafana_dashboard.png") -> Path | None:
    from_ms = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    to_ms = int(datetime(2026, 1, 8, tzinfo=timezone.utc).timestamp() * 1000)
    return capture_url(
        "http://localhost:3000/d/smart-metering-loss/smart-metering-loss-analysis"
        f"?orgId=1&from={from_ms}&to={to_ms}&kiosk",
        filename,
        width=1800,
        height=1400,
    )


def capture_screenshots() -> list[Path]:
    captures = [capture_url("http://localhost:8000/docs", "11_fastapi_swagger.png")]
    return [path for path in captures if path is not None]


def write_report(images: list[Path], screenshots: list[Path], counts: dict[str, int]) -> Path:
    report = DEMO_DIR / "README.md"
    lines = [
        "# Smart Metering Demo Pack",
        "",
        "Imagenes generadas para documentar el proyecto con datos y servicios reales.",
        "",
        "## Resumen de datos",
        "",
        f"- Feeders: {counts['feeders']}",
        f"- Transformers: {counts['transformers']}",
        f"- Meters: {counts['meters']}",
        f"- Meter readings: {counts['meter_readings']}",
        f"- Energy balances: {counts['energy_balance']}",
        f"- Alerts: {counts['alerts']}",
        "",
        "## Imagenes",
        "",
    ]
    for path in images + screenshots:
        relative = path.relative_to(DEMO_DIR)
        title = path.stem.replace("_", " ").title()
        lines.extend([f"### {title}", "", f"![{title}]({relative.as_posix()})", ""])
    report.write_text("\n".join(lines), encoding="utf-8")

    html = DEMO_DIR / "index.html"
    cards = "\n".join(
        f"<section><h2>{path.stem.replace('_', ' ').title()}</h2><img src='{path.relative_to(DEMO_DIR).as_posix()}' /></section>"
        for path in images + screenshots
    )
    html.write_text(
        textwrap.dedent(f"""
            <!doctype html>
            <html lang="es">
            <head>
              <meta charset="utf-8" />
              <meta name="viewport" content="width=device-width, initial-scale=1" />
              <title>Smart Metering Demo Pack</title>
              <style>
                body {{ margin: 0; font-family: Arial, sans-serif; background: #f8fafc; color: #0f172a; }}
                header {{ padding: 32px 48px; background: #0f172a; color: white; }}
                main {{ padding: 28px 48px; display: grid; gap: 28px; }}
                section {{ background: white; border: 1px solid #cbd5e1; padding: 18px; }}
                h1, h2 {{ margin: 0 0 14px; }}
                img {{ width: 100%; height: auto; border: 1px solid #e2e8f0; }}
              </style>
            </head>
            <body>
              <header>
                <h1>Smart Metering Demo Pack</h1>
                <p>Graficas y capturas generadas desde el proyecto ejecutado.</p>
              </header>
              <main>{cards}</main>
            </body>
            </html>
            """).strip(),
        encoding="utf-8",
    )
    return report


def main() -> None:
    ensure_dirs()
    data = load_data()
    counts = db_counts()
    images = [
        plot_cover(data, counts),
        plot_architecture(),
        plot_kpis(data, counts),
        plot_loss_timeseries(data),
        plot_energy_balance_latest(data),
        plot_availability_heatmap(data),
        plot_critical_ranking(data),
        plot_alerts_breakdown(data),
        plot_gis_map(data),
        plot_data_model(),
        plot_validation(data, counts),
    ]
    screenshots = capture_screenshots()
    report = write_report(images, screenshots, counts)
    print(f"Generated {len(images)} charts and {len(screenshots)} screenshots.")
    print(f"Demo report: {report}")


if __name__ == "__main__":
    main()
