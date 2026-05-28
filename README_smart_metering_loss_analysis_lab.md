# Smart Metering & Loss Analysis Lab

**Laboratorio reproducible de macromedición, telemedición y análisis de pérdidas eléctricas con herramientas gratuitas**

> Proyecto aplicado de portafolio desarrollado en Visual Studio Code con GitHub Copilot, Python, OpenDSS, PostgreSQL/PostGIS, QGIS, Grafana OSS, Node-RED, MQTT/Mosquitto, PyModbus, Gurux DLMS/COSEM y datos sintéticos.

---

## 1. Resumen ejecutivo

Este proyecto construye un laboratorio técnico reproducible para simular, almacenar, analizar y visualizar información asociada a macromedición y telemedición eléctrica en una red de distribución simulada.

El objetivo no es conectarse a infraestructura real de una empresa de energía, sino demostrar dominio conceptual y técnico sobre:

- macromedición;
- medición inteligente;
- telemedición;
- reducción y análisis de pérdidas;
- balances de energía;
- comunicación de medidores;
- indicadores operativos;
- análisis geográfico de activos;
- validación de lecturas;
- detección de anomalías;
- visualización en dashboards;
- documentación técnica reproducible.

El proyecto se presenta como un **caso de estudio técnico validado por simulación y escenarios controlados**, adecuado para portafolio profesional y para sustentar competencias en un cargo de **Profesional de Macromedición**.

---

## 2. Problema que aborda

En sistemas de distribución eléctrica, las empresas necesitan conocer cuánta energía ingresa a una zona, circuito, transformador o sector, y cuánta energía es efectivamente registrada por los puntos de medición aguas abajo.

Cuando existe diferencia entre la energía suministrada y la energía medida, pueden aparecer pérdidas técnicas, pérdidas no técnicas, fallas de comunicación, errores de medición, datos incompletos o problemas de cobertura de macromedición.

Este laboratorio reproduce ese contexto mediante una red simulada y datos sintéticos, para analizar:

- energía suministrada por alimentador o transformador;
- energía registrada por medidores;
- pérdidas estimadas en kWh;
- porcentaje de pérdidas;
- disponibilidad de telemedición;
- medidores sin comunicación;
- lecturas faltantes;
- lecturas atípicas;
- alertas por sector;
- visualización geográfica de zonas críticas.

---

## 3. Objetivo general

Diseñar e implementar un prototipo reproducible para análisis de macromedición, telemedición y pérdidas de energía en redes de distribución eléctrica, utilizando herramientas gratuitas, datos sintéticos y escenarios controlados de validación.

---

## 4. Objetivos específicos

1. Simular una red de distribución eléctrica con alimentadores, transformadores, cargas y puntos de medición.
2. Generar datos sintéticos de lecturas de energía para medidores y macromedidores.
3. Modelar eventos de telemedición como lecturas faltantes, fallas de comunicación y datos atípicos.
4. Calcular balances energéticos por transformador, alimentador o sector.
5. Estimar pérdidas en kWh y porcentaje de pérdidas.
6. Almacenar activos, lecturas, eventos e indicadores en una base de datos relacional y geoespacial.
7. Visualizar activos eléctricos en mapas mediante QGIS.
8. Construir dashboards operativos con Grafana OSS y opcionalmente Power BI Desktop.
9. Simular transmisión de lecturas por MQTT y Modbus.
10. Documentar arquitectura, modelo de datos, escenarios de validación, indicadores y resultados.

---

## 5. Alcance del proyecto

### Incluido

- Red eléctrica simulada.
- Datos sintéticos realistas.
- Macromedidores simulados.
- Medidores inteligentes simulados.
- Transformadores, alimentadores y sectores.
- Base de datos PostgreSQL/PostGIS.
- Procesamiento en Python.
- Visualización en Grafana.
- Mapa en QGIS.
- Simulación de telemedición con MQTT.
- Simulación básica Modbus.
- Exploración DLMS/COSEM con Gurux.
- Documentación técnica.
- Evidencias para portafolio.

### No incluido

- Conexión a medidores reales.
- Integración con SCADA empresarial.
- Integración real con HES o MDMS comercial.
- Validación en campo.
- Certificación oficial de pérdidas de energía.
- Uso de herramientas propietarias empresariales como Oracle Utilities MDM, PrimeStone, Itron, Siemens EnergyIP o Landis+Gyr HES.

---

## 6. Herramientas gratuitas del proyecto

| Componente | Herramienta | Uso |
|---|---|---|
| IDE | Visual Studio Code | Desarrollo del repositorio |
| Asistente de programación | GitHub Copilot | Apoyo para generar, explicar y refactorizar código |
| Lenguaje principal | Python | Procesamiento, simulación, análisis y APIs |
| Simulación eléctrica | OpenDSS | Simulación de red de distribución |
| Interfaz Python-OpenDSS | OpenDSSDirect.py | Ejecución de OpenDSS desde Python |
| Base de datos | PostgreSQL | Persistencia de activos, lecturas e indicadores |
| Geodatos | PostGIS | Ubicación de medidores, transformadores y sectores |
| Cliente SQL | DBeaver Community | Consulta y administración visual de datos |
| GIS | QGIS | Visualización geográfica |
| Dashboards | Grafana OSS | Indicadores, series de tiempo y alertas |
| Dashboard opcional | Power BI Desktop | Reporte local opcional |
| Telemetría IoT | Node-RED | Flujos visuales de telemedición |
| Broker MQTT | Eclipse Mosquitto | Mensajería para lecturas simuladas |
| Series de tiempo opcional | InfluxDB 3 Core | Almacenamiento de lecturas temporales |
| Protocolo industrial | PyModbus | Simulación de cliente/servidor Modbus |
| Medición inteligente | Gurux DLMS/COSEM | Exploración de comunicación DLMS |
| Análisis de red | Wireshark | Captura de tráfico MQTT/Modbus |
| Contenedores | Docker Compose | Levantar servicios reproducibles |

---

## 7. Arquitectura propuesta

```text
                           +--------------------------+
                           |   OpenDSS / Python       |
                           |   Red simulada           |
                           +------------+-------------+
                                        |
                                        v
+------------------+        +--------------------------+
| Node-RED         | MQTT   | Python Data Generator    |
| Flujos IoT       +------->| Lecturas sintéticas      |
+--------+---------+        +------------+-------------+
         |                               |
         |                               v
         |                    +--------------------------+
         |                    | PostgreSQL + PostGIS     |
         |                    | Activos, lecturas,       |
         |                    | eventos, indicadores     |
         |                    +------+-------------+-----+
         |                           |             |
         v                           v             v
+------------------+        +----------------+  +----------------+
| Mosquitto MQTT   |        | Grafana OSS    |  | QGIS           |
| Broker           |        | Dashboards     |  | Mapa activos   |
+------------------+        +----------------+  +----------------+

Componentes opcionales:
- InfluxDB 3 Core para series de tiempo.
- PyModbus para simular lecturas industriales.
- Gurux DLMS/COSEM para explorar medición inteligente.
- FastAPI para exponer indicadores mediante API REST.
```

---

## 8. Indicadores técnicos

| Indicador | Fórmula / lógica | Interpretación |
|---|---|---|
| Energía suministrada | Lectura del macromedidor de entrada | Energía que entra a un sector |
| Energía medida | Suma de medidores asociados | Energía registrada aguas abajo |
| Pérdida kWh | Energía suministrada - energía medida | Diferencia absoluta |
| Pérdida % | Pérdida kWh / energía suministrada * 100 | Nivel relativo de pérdida |
| Disponibilidad de lecturas | Lecturas recibidas / lecturas esperadas * 100 | Calidad de telemedición |
| Medidores sin comunicación | Medidores sin lectura en ventana temporal | Posible falla de comunicación |
| Lecturas atípicas | Umbral estadístico o regla de negocio | Posible error o consumo anómalo |
| Sectores críticos | Pérdida % superior al umbral | Prioridad operativa |
| Calidad de datos | Completitud, consistencia y rango válido | Confiabilidad del dato |

---

## 9. Estructura recomendada del repositorio

```text
smart-metering-loss-analysis-lab/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── requirements.txt
│
├── data/
│   ├── raw/
│   ├── synthetic/
│   │   ├── meters.csv
│   │   ├── transformers.csv
│   │   ├── feeders.csv
│   │   ├── readings.csv
│   │   └── communication_events.csv
│   └── processed/
│       ├── energy_balance.csv
│       └── alerts.csv
│
├── opendss/
│   ├── master.dss
│   ├── feeders.dss
│   ├── transformers.dss
│   ├── loads.dss
│   ├── meters.dss
│   └── loadshape.dss
│
├── sql/
│   ├── 01_extensions.sql
│   ├── 02_schema.sql
│   ├── 03_views.sql
│   ├── 04_seed_assets.sql
│   └── 05_quality_queries.sql
│
├── src/
│   ├── config.py
│   ├── generate_assets.py
│   ├── generate_synthetic_readings.py
│   ├── simulate_meter_failures.py
│   ├── calculate_energy_balance.py
│   ├── detect_anomalies.py
│   ├── database_loader.py
│   ├── mqtt_publisher.py
│   ├── mqtt_consumer.py
│   ├── modbus_server.py
│   ├── modbus_client.py
│   ├── opendss_runner.py
│   └── api.py
│
├── dashboards/
│   ├── grafana/
│   └── powerbi/
│
├── maps/
│   ├── qgis_project.qgz
│   ├── assets.geojson
│   └── README.md
│
├── docs/
│   ├── 01_architecture.md
│   ├── 02_data_model.md
│   ├── 03_validation_scenarios.md
│   ├── 04_indicators.md
│   ├── 05_copilot_workflow.md
│   ├── 06_interview_explanation.md
│   └── screenshots/
│
└── tests/
    ├── test_energy_balance.py
    ├── test_anomaly_detection.py
    ├── test_data_quality.py
    └── test_synthetic_generator.py
```

---

## 10. Instalación del entorno

### Requisitos base

- Visual Studio Code.
- Git.
- Docker Desktop o Docker Engine.
- Python 3.11 o superior.
- Extensión Python para VS Code.
- Extensión GitHub Copilot para VS Code.
- QGIS.
- DBeaver Community.
- Wireshark.

### Crear entorno Python

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## 11. Archivo requirements.txt recomendado

```txt
pandas
numpy
sqlalchemy
psycopg2-binary
python-dotenv
pydantic
fastapi
uvicorn
paho-mqtt
pymodbus
opendssdirect.py
geopandas
shapely
pytest
ruff
black
matplotlib
```

---

## 12. Docker Compose propuesto

Archivo: `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: sm_postgres
    environment:
      POSTGRES_DB: smart_metering
      POSTGRES_USER: smart
      POSTGRES_PASSWORD: smartpass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql:/docker-entrypoint-initdb.d

  grafana:
    image: grafana/grafana-oss:latest
    container_name: sm_grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana

  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: sm_mosquitto
    ports:
      - "1883:1883"
    volumes:
      - ./mqtt/mosquitto.conf:/mosquitto/config/mosquitto.conf

  nodered:
    image: nodered/node-red:latest
    container_name: sm_nodered
    ports:
      - "1880:1880"
    volumes:
      - nodered_data:/data
    depends_on:
      - mosquitto

  influxdb:
    image: influxdb:2
    container_name: sm_influxdb
    ports:
      - "8086:8086"
    volumes:
      - influx_data:/var/lib/influxdb2

volumes:
  postgres_data:
  grafana_data:
  nodered_data:
  influx_data:
```

Archivo: `mqtt/mosquitto.conf`

```conf
listener 1883
allow_anonymous true
```

Ejecutar:

```bash
docker compose up -d
docker compose ps
```

---

## 13. Modelo de datos

### Entidades principales

- `feeders`: alimentadores.
- `transformers`: transformadores.
- `meters`: medidores.
- `meter_readings`: lecturas de medidores.
- `macro_readings`: lecturas de macromedidores.
- `communication_events`: eventos de comunicación.
- `energy_balance`: balances de energía.
- `alerts`: alertas operativas.

Archivo: `sql/01_extensions.sql`

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Archivo: `sql/02_schema.sql`

```sql
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
    energy_kwh NUMERIC(14,4) NOT NULL,
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
    input_energy_kwh NUMERIC(14,4) NOT NULL,
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
```

Archivo: `sql/03_views.sql`

```sql
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
```

---

## 14. Código base: generación de activos

Archivo: `src/generate_assets.py`

```python
from pathlib import Path
import random
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "data" / "synthetic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

POPAYAN_LAT = 2.4448
POPAYAN_LON = -76.6147


def jitter(value: float, delta: float = 0.02) -> float:
    return value + random.uniform(-delta, delta)


def generate_assets(feeders_count=2, transformers_per_feeder=3, meters_per_transformer=12):
    feeders, transformers, meters = [], [], []

    for f in range(1, feeders_count + 1):
        feeder_id = f"FD-{f:02d}"
        feeders.append({
            "feeder_id": feeder_id,
            "name": f"Feeder {f}",
            "voltage_kv": 13.2,
            "zone": f"Zone {f}",
            "lat": jitter(POPAYAN_LAT),
            "lon": jitter(POPAYAN_LON),
        })

        for t in range(1, transformers_per_feeder + 1):
            transformer_id = f"TR-{f:02d}-{t:02d}"
            transformers.append({
                "transformer_id": transformer_id,
                "feeder_id": feeder_id,
                "name": f"Transformer {f}-{t}",
                "capacity_kva": random.choice([75, 112.5, 150, 225]),
                "sector": f"S-{f}-{t}",
                "lat": jitter(POPAYAN_LAT),
                "lon": jitter(POPAYAN_LON),
            })

            meters.append({
                "meter_id": f"MM-{f:02d}-{t:02d}",
                "transformer_id": transformer_id,
                "customer_type": "MACRO",
                "is_macro": True,
                "communication_type": "MQTT",
                "installation_status": "ACTIVE",
                "lat": jitter(POPAYAN_LAT, 0.01),
                "lon": jitter(POPAYAN_LON, 0.01),
            })

            for m in range(1, meters_per_transformer + 1):
                meters.append({
                    "meter_id": f"SM-{f:02d}-{t:02d}-{m:03d}",
                    "transformer_id": transformer_id,
                    "customer_type": random.choice(["RESIDENTIAL", "COMMERCIAL", "SMALL_INDUSTRY"]),
                    "is_macro": False,
                    "communication_type": random.choice(["MQTT", "MODBUS_TCP", "DLMS_SIM"]),
                    "installation_status": "ACTIVE",
                    "lat": jitter(POPAYAN_LAT, 0.015),
                    "lon": jitter(POPAYAN_LON, 0.015),
                })

    pd.DataFrame(feeders).to_csv(OUT_DIR / "feeders.csv", index=False)
    pd.DataFrame(transformers).to_csv(OUT_DIR / "transformers.csv", index=False)
    pd.DataFrame(meters).to_csv(OUT_DIR / "meters.csv", index=False)


if __name__ == "__main__":
    generate_assets()
    print("Synthetic assets generated.")
```

---

## 15. Código base: lecturas sintéticas

Archivo: `src/generate_synthetic_readings.py`

```python
from pathlib import Path
import random
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"


def customer_base_load(customer_type: str) -> float:
    if customer_type == "RESIDENTIAL":
        return random.uniform(0.25, 1.8)
    if customer_type == "COMMERCIAL":
        return random.uniform(1.2, 5.5)
    if customer_type == "SMALL_INDUSTRY":
        return random.uniform(3.5, 12.0)
    return random.uniform(0.5, 2.0)


def daily_profile_multiplier(hour: int) -> float:
    if 0 <= hour <= 5:
        return 0.45
    if 6 <= hour <= 8:
        return 0.85
    if 9 <= hour <= 17:
        return 1.00
    if 18 <= hour <= 22:
        return 1.35
    return 0.75


def generate_readings(days: int = 30, loss_factor_range=(0.04, 0.18)) -> None:
    meters = pd.read_csv(DATA_DIR / "meters.csv")
    smart_meters = meters[meters["is_macro"] == False].copy()
    timestamps = pd.date_range("2026-01-01 00:00:00", periods=days * 24, freq="h")

    readings, macro_readings = [], []

    for _, meter in smart_meters.iterrows():
        base_load = customer_base_load(meter["customer_type"])

        for ts in timestamps:
            if random.random() < 0.03:  # falla de comunicación
                continue

            energy = base_load * daily_profile_multiplier(ts.hour) * np.random.normal(1.0, 0.10)
            quality_flag = "OK"

            if random.random() < 0.01:  # anomalía
                energy *= random.choice([0.1, 4.5])
                quality_flag = "ANOMALY"

            readings.append({
                "meter_id": meter["meter_id"],
                "reading_timestamp": ts,
                "energy_kwh": round(max(energy, 0.01), 4),
                "voltage_v": round(np.random.normal(120, 4), 2),
                "current_a": round(np.random.normal(12, 3), 2),
                "power_factor": round(min(max(np.random.normal(0.93, 0.03), 0.7), 1.0), 3),
                "quality_flag": quality_flag,
                "source": "synthetic",
            })

    readings_df = pd.DataFrame(readings)

    enriched = readings_df.merge(meters[["meter_id", "transformer_id"]], on="meter_id", how="left")
    for (transformer_id, ts), group in enriched.groupby(["transformer_id", "reading_timestamp"]):
        measured = group["energy_kwh"].sum()
        loss_factor = random.uniform(*loss_factor_range)
        input_energy = measured / (1 - loss_factor)
        macro_readings.append({
            "transformer_id": transformer_id,
            "reading_timestamp": ts,
            "input_energy_kwh": round(input_energy, 4),
            "quality_flag": "OK",
            "source": "synthetic",
        })

    readings_df.to_csv(DATA_DIR / "readings.csv", index=False)
    pd.DataFrame(macro_readings).to_csv(DATA_DIR / "macro_readings.csv", index=False)


if __name__ == "__main__":
    generate_readings()
    print("Synthetic meter readings generated.")
```

---

## 16. Código base: balance energético

Archivo: `src/calculate_energy_balance.py`

```python
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_energy_balance() -> pd.DataFrame:
    meters = pd.read_csv(DATA_DIR / "meters.csv")
    readings = pd.read_csv(DATA_DIR / "readings.csv", parse_dates=["reading_timestamp"])
    macro = pd.read_csv(DATA_DIR / "macro_readings.csv", parse_dates=["reading_timestamp"])

    smart_meters = meters[meters["is_macro"] == False][["meter_id", "transformer_id"]]
    readings = readings.merge(smart_meters, on="meter_id", how="left")

    measured = readings.groupby(["transformer_id", "reading_timestamp"]).agg(
        measured_energy_kwh=("energy_kwh", "sum"),
        received_readings=("meter_id", "count"),
    ).reset_index()

    expected = smart_meters.groupby("transformer_id").agg(
        expected_readings=("meter_id", "count")
    ).reset_index()

    balance = macro.merge(measured, on=["transformer_id", "reading_timestamp"], how="left")
    balance = balance.merge(expected, on="transformer_id", how="left")

    balance["measured_energy_kwh"] = balance["measured_energy_kwh"].fillna(0)
    balance["received_readings"] = balance["received_readings"].fillna(0)
    balance["loss_kwh"] = balance["input_energy_kwh"] - balance["measured_energy_kwh"]
    balance["loss_percent"] = (balance["loss_kwh"] / balance["input_energy_kwh"]) * 100
    balance["reading_availability_percent"] = (balance["received_readings"] / balance["expected_readings"]) * 100

    balance.to_csv(OUT_DIR / "energy_balance.csv", index=False)
    return balance


if __name__ == "__main__":
    print(calculate_energy_balance().head())
```

---

## 17. Código base: detección de anomalías

Archivo: `src/detect_anomalies.py`

```python
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def detect_anomalies(loss_threshold_percent=12.0, availability_threshold_percent=95.0) -> pd.DataFrame:
    balance = pd.read_csv(PROCESSED_DIR / "energy_balance.csv", parse_dates=["reading_timestamp"])
    readings = pd.read_csv(DATA_DIR / "readings.csv", parse_dates=["reading_timestamp"])
    alerts = []

    for _, row in balance[balance["loss_percent"] > loss_threshold_percent].iterrows():
        alerts.append({
            "entity_type": "TRANSFORMER",
            "entity_id": row["transformer_id"],
            "alert_timestamp": row["reading_timestamp"],
            "alert_type": "HIGH_LOSS",
            "alert_message": f"Loss percent {row['loss_percent']:.2f}% exceeds threshold.",
            "severity": "HIGH",
        })

    for _, row in balance[balance["reading_availability_percent"] < availability_threshold_percent].iterrows():
        alerts.append({
            "entity_type": "TRANSFORMER",
            "entity_id": row["transformer_id"],
            "alert_timestamp": row["reading_timestamp"],
            "alert_type": "LOW_READING_AVAILABILITY",
            "alert_message": f"Reading availability {row['reading_availability_percent']:.2f}% below threshold.",
            "severity": "MEDIUM",
        })

    for _, row in readings[readings["quality_flag"] == "ANOMALY"].iterrows():
        alerts.append({
            "entity_type": "METER",
            "entity_id": row["meter_id"],
            "alert_timestamp": row["reading_timestamp"],
            "alert_type": "ANOMALOUS_READING",
            "alert_message": f"Anomalous reading detected: {row['energy_kwh']} kWh.",
            "severity": "MEDIUM",
        })

    alerts_df = pd.DataFrame(alerts)
    alerts_df.to_csv(PROCESSED_DIR / "alerts.csv", index=False)
    return alerts_df


if __name__ == "__main__":
    print(detect_anomalies().head())
```

---

## 18. Código base: MQTT

Archivo: `src/mqtt_publisher.py`

```python
from pathlib import Path
import json
import time
import pandas as pd
import paho.mqtt.client as mqtt

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"
MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC_PREFIX = "smart-metering/readings"


def publish_readings(delay_seconds=0.05, max_messages=500):
    readings = pd.read_csv(DATA_DIR / "readings.csv")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    for _, row in readings.head(max_messages).iterrows():
        payload = {
            "meter_id": row["meter_id"],
            "timestamp": row["reading_timestamp"],
            "energy_kwh": row["energy_kwh"],
            "voltage_v": row["voltage_v"],
            "current_a": row["current_a"],
            "power_factor": row["power_factor"],
            "quality_flag": row["quality_flag"],
        }
        topic = f"{TOPIC_PREFIX}/{row['meter_id']}"
        client.publish(topic, json.dumps(payload))
        print(f"Published to {topic}: {payload}")
        time.sleep(delay_seconds)

    client.disconnect()


if __name__ == "__main__":
    publish_readings()
```

Archivo: `src/mqtt_consumer.py`

```python
import json
import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC = "smart-metering/readings/#"


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with reason code: {reason_code}")
    client.subscribe(TOPIC)


def on_message(client, userdata, message):
    payload = json.loads(message.payload.decode("utf-8"))
    print(f"Topic: {message.topic}")
    print(payload)


def run_consumer():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    run_consumer()
```

---

## 19. Código base: OpenDSS

Archivo: `opendss/master.dss`

```text
Clear

New Circuit.SimpleFeeder basekv=13.2 pu=1.0 phases=3 bus1=sourcebus
New Transformer.TR1 phases=3 windings=2 buses=[sourcebus, loadbus] conns=[wye,wye] kvs=[13.2,0.208] kvas=[150,150] xhl=4
New Linecode.LC1 nphases=3 r1=0.642 x1=0.083 r0=0.961 x0=0.255 units=km
New Line.L1 phases=3 bus1=loadbus bus2=busload linecode=LC1 length=0.5 units=km
New Load.Load1 bus1=busload phases=3 conn=wye kv=0.208 kw=50 kvar=10
New EnergyMeter.M1 element=Transformer.TR1 terminal=1

Set VoltageBases=[13.2,0.208]
CalcVoltageBases
Solve

Show Voltages
Show Powers
```

Archivo: `src/opendss_runner.py`

```python
from pathlib import Path
import opendssdirect as dss

BASE_DIR = Path(__file__).resolve().parents[1]
DSS_FILE = BASE_DIR / "opendss" / "master.dss"


def run_opendss():
    dss.Text.Command(f"Redirect {DSS_FILE}")
    dss.Solution.Solve()
    print("Circuit:", dss.Circuit.Name())
    print("Total power:", dss.Circuit.TotalPower())
    print("All bus names:", dss.Circuit.AllBusNames())


if __name__ == "__main__":
    run_opendss()
```

---

## 20. API opcional con FastAPI

Archivo: `src/api.py`

```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://smart:smartpass@localhost:5432/smart_metering",
)

app = FastAPI(title="Smart Metering Loss Analysis API")
engine = create_engine(DATABASE_URL)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/balances/latest")
def latest_balances():
    query = """
        SELECT transformer_id, transformer_name, sector, reading_timestamp,
               input_energy_kwh, measured_energy_kwh, loss_kwh,
               loss_percent, reading_availability_percent
        FROM v_transformer_latest_balance
        ORDER BY loss_percent DESC
    """
    with engine.begin() as conn:
        rows = conn.execute(text(query)).mappings().all()
    return list(rows)


@app.get("/alerts/open")
def open_alerts():
    query = """
        SELECT entity_type, entity_id, alert_timestamp,
               alert_type, alert_message, severity, status
        FROM v_open_alerts
        ORDER BY alert_timestamp DESC
    """
    with engine.begin() as conn:
        rows = conn.execute(text(query)).mappings().all()
    return list(rows)
```

Ejecutar:

```bash
uvicorn src.api:app --reload
```

Abrir:

```text
http://localhost:8000/docs
```

---

## 21. Pruebas automatizadas

Archivo: `tests/test_energy_balance.py`

```python
def test_loss_calculation():
    input_energy = 100.0
    measured_energy = 85.0
    loss_kwh = input_energy - measured_energy
    loss_percent = (loss_kwh / input_energy) * 100
    assert loss_kwh == 15.0
    assert loss_percent == 15.0


def test_availability_calculation():
    expected_readings = 10
    received_readings = 9
    availability = (received_readings / expected_readings) * 100
    assert availability == 90.0
```

Ejecutar:

```bash
pytest
```

---

## 22. Flujo de ejecución del MVP

```bash
docker compose up -d
python src/generate_assets.py
python src/generate_synthetic_readings.py
python src/calculate_energy_balance.py
python src/detect_anomalies.py
pytest
```

Después:

```bash
python src/mqtt_consumer.py
python src/mqtt_publisher.py
uvicorn src.api:app --reload
```

URLs locales:

```text
Grafana:  http://localhost:3000
Node-RED: http://localhost:1880
FastAPI:  http://localhost:8000/docs
```

---

## 23. Dashboard recomendado en Grafana

Crear datasource PostgreSQL:

- Host: `postgres:5432` si Grafana corre en Docker.
- Database: `smart_metering`.
- User: `smart`.
- Password: `smartpass`.
- TLS/SSL: disabled para entorno local.

Paneles:

1. **Pérdida porcentual por transformador**

```sql
SELECT
    reading_timestamp AS time,
    transformer_id,
    loss_percent
FROM energy_balance
ORDER BY reading_timestamp;
```

2. **Energía de entrada vs energía medida**

```sql
SELECT
    reading_timestamp AS time,
    transformer_id,
    input_energy_kwh,
    measured_energy_kwh
FROM energy_balance
ORDER BY reading_timestamp;
```

3. **Disponibilidad de lecturas**

```sql
SELECT
    reading_timestamp AS time,
    transformer_id,
    reading_availability_percent
FROM energy_balance
ORDER BY reading_timestamp;
```

4. **Ranking de sectores críticos**

```sql
SELECT
    transformer_id,
    AVG(loss_percent) AS avg_loss_percent
FROM energy_balance
GROUP BY transformer_id
ORDER BY avg_loss_percent DESC;
```

5. **Alertas abiertas**

```sql
SELECT
    alert_timestamp,
    entity_type,
    entity_id,
    alert_type,
    severity,
    alert_message
FROM alerts
WHERE status = 'OPEN'
ORDER BY alert_timestamp DESC;
```

---

## 24. Mapa recomendado en QGIS

Capas mínimas:

- Alimentadores.
- Transformadores.
- Medidores.
- Sectores.
- Alertas por transformador.
- Pérdida promedio por sector.

Conexión desde QGIS a PostGIS:

1. Abrir QGIS.
2. Ir a `Browser > PostgreSQL > New Connection`.
3. Host: `localhost`.
4. Port: `5432`.
5. Database: `smart_metering`.
6. User: `smart`.
7. Password: `smartpass`.
8. Cargar tablas `feeders`, `transformers` y `meters`.

Simbología sugerida:

- Medidores normales: puntos pequeños.
- Macromedidores: puntos destacados.
- Transformadores con pérdida alta: color por rango.
- Sectores críticos: categorización por pérdida porcentual.

---

## 25. Escenarios de validación

| Escenario | Descripción | Resultado esperado |
|---|---|---|
| E01 | Operación normal | Pérdida baja y disponibilidad alta |
| E02 | Medidor sin comunicación | Baja disponibilidad de lecturas |
| E03 | Lectura atípica | Alerta de lectura anómala |
| E04 | Sector con pérdida alta | Alerta HIGH_LOSS |
| E05 | Datos incompletos | Alertas por calidad de datos |
| E06 | Macromedidor con lectura normal | Balance calculado correctamente |
| E07 | Transformador con varios clientes | Suma de medidores asociada correctamente |
| E08 | Flujo MQTT activo | Lecturas publicadas y consumidas |
| E09 | Simulación Modbus | Registros consultados desde cliente |
| E10 | Visualización GIS | Activos visibles en QGIS |

---

## 26. Criterios de aceptación

| Criterio | Condición de aceptación |
|---|---|
| Repositorio ejecutable | El proyecto corre localmente siguiendo el README |
| Datos sintéticos | Se generan activos y lecturas sin errores |
| Base de datos | PostgreSQL/PostGIS almacena activos, lecturas e indicadores |
| Balance energético | Se calcula pérdida kWh y pérdida % |
| Calidad de datos | Se detectan lecturas faltantes y atípicas |
| Telemedición | MQTT publica y consume lecturas simuladas |
| Dashboard | Grafana muestra al menos cinco paneles operativos |
| GIS | QGIS muestra medidores, transformadores y sectores |
| Pruebas | `pytest` ejecuta pruebas de cálculo y calidad |
| Documentación | Hay arquitectura, modelo de datos, escenarios y capturas |

---

## 27. Flujo con GitHub Copilot en VS Code

No usar Copilot para “hacer todo el proyecto”. Usarlo como asistente por tareas pequeñas, revisables y testeables.

Prompts útiles:

```text
Create a Python script that generates synthetic hourly energy readings for smart meters, including missing values, communication failures and anomalous values.
```

```text
Create a PostgreSQL/PostGIS schema for feeders, transformers, smart meters, meter readings, macro meter readings, communication events, energy balances and alerts.
```

```text
Write a Python function to calculate energy losses by transformer using input energy and the sum of downstream meter readings.
```

```text
Create pytest unit tests for energy balance calculation, including normal cases, missing readings and zero input energy.
```

```text
Create a Grafana PostgreSQL query to show loss percentage by transformer over time.
```

```text
Review this Python function and suggest improvements for readability, validation and error handling.
```

Reglas de control:

- Revisar siempre el código generado.
- Ejecutar pruebas después de aceptar cambios.
- No aceptar código que no entiendas.
- Pedir a Copilot explicación de funciones complejas.
- Crear commits pequeños.
- Documentar decisiones técnicas.
- Mantener datos sintéticos claramente marcados como simulados.

---

## 28. Roadmap de desarrollo

### Fase 1 — MVP básico

- Crear repositorio.
- Crear entorno Python.
- Crear Docker Compose con PostgreSQL/PostGIS, Grafana, Mosquitto y Node-RED.
- Crear esquema SQL.
- Generar activos sintéticos.
- Generar lecturas sintéticas.
- Calcular balance de energía.
- Detectar alertas simples.
- Crear primer dashboard.

Resultado: proyecto defendible para entrevista.

### Fase 2 — GIS y telemedición

- Crear geometrías de activos.
- Conectar QGIS a PostGIS.
- Simular MQTT.
- Crear flujos Node-RED.
- Agregar eventos de comunicación.
- Visualizar medidores sin comunicación.

Resultado: proyecto más alineado a telemedición y cobertura.

### Fase 3 — Simulación eléctrica

- Crear caso básico OpenDSS.
- Ejecutar OpenDSS desde Python.
- Relacionar resultados de simulación con lecturas sintéticas.
- Documentar diferencias entre red simulada y medición sintética.

Resultado: mayor fuerza técnica en distribución eléctrica.

### Fase 4 — Protocolos

- Agregar PyModbus server/client.
- Capturar tráfico con Wireshark.
- Explorar Gurux DLMS/COSEM.
- Documentar diferencias entre MQTT, Modbus y DLMS/COSEM.

Resultado: evidencia de conocimiento en sistemas de comunicación.

### Fase 5 — API y entrega final

- Crear API con FastAPI.
- Exponer últimos balances y alertas.
- Agregar pruebas unitarias.
- Crear informe PDF.
- Grabar video demo de 3 a 5 minutos.
- Preparar explicación para entrevista.

Resultado: portafolio técnico completo.

---

## 29. Evidencias para portafolio

Guardar en `docs/screenshots/`:

1. Estructura del repositorio en VS Code.
2. Docker Compose corriendo.
3. Tablas en DBeaver.
4. Dashboard de Grafana.
5. Mapa en QGIS.
6. Flujo Node-RED.
7. Publicación MQTT.
8. Prueba Modbus.
9. Ejecución de pytest.
10. Swagger de FastAPI.
11. Resultado de OpenDSS.
12. Captura de Wireshark con tráfico MQTT o Modbus.

---

## 30. Explicación corta para entrevista

> Desarrollé un laboratorio reproducible de macromedición y telemedición eléctrica usando herramientas gratuitas. El proyecto simula una red de distribución, genera lecturas sintéticas de medidores, calcula balances de energía por transformador, estima pérdidas, detecta lecturas faltantes o atípicas y visualiza indicadores en dashboards. También incluye componentes de telemedición mediante MQTT, simulación Modbus, base de datos PostgreSQL/PostGIS y visualización geográfica en QGIS. Lo construí como caso de estudio técnico para demostrar capacidades en análisis de datos, sistemas de comunicación, medición inteligente y eficiencia operativa en redes de distribución.

---

## 31. Versión para CV

**Proyecto aplicado de portafolio — Laboratorio reproducible de macromedición, telemedición y análisis de pérdidas eléctricas**

- Desarrollo de un laboratorio técnico en Visual Studio Code para análisis de macromedición y telemedición eléctrica, usando herramientas gratuitas y datos sintéticos.
- Implementación de simulación de red y medición con Python, OpenDSS, PostgreSQL/PostGIS, QGIS, Grafana OSS, Node-RED, MQTT/Mosquitto, PyModbus y Gurux DLMS/COSEM.
- Cálculo de balances energéticos por transformador, pérdidas estimadas, disponibilidad de lecturas, alertas por comunicación y detección de datos atípicos.
- Construcción de dashboards operativos, visualización geográfica de activos y documentación técnica como evidencia de portafolio.

---

## 32. Buenas prácticas

- Marcar todos los datos como sintéticos.
- Documentar supuestos.
- No afirmar validación en campo.
- No afirmar integración con medidores reales.
- Usar lenguaje de “simulación”, “escenarios controlados” y “prototipo reproducible”.
- Citar herramientas oficiales en el README.
- Mantener un demo funcional antes de agregar módulos avanzados.
- Priorizar claridad sobre complejidad.
- Usar pruebas unitarias para validar cálculos.
- Crear un informe corto con resultados.

---

## 33. Referencias oficiales para estudio

- OpenDSS - EPRI: https://opendss.epri.com/
- OpenDSSDirect.py: https://dss-extensions.org/OpenDSSDirect.py/
- PostgreSQL License: https://www.postgresql.org/about/licence/
- PostGIS: https://postgis.net/
- QGIS Documentation: https://docs.qgis.org/latest/en/docs/index.html
- Grafana OSS: https://grafana.com/oss/
- Node-RED: https://nodered.org/
- Eclipse Mosquitto: https://mosquitto.org/
- PyModbus Documentation: https://pymodbus.readthedocs.io/
- DLMS UA Core Specifications: https://www.dlms.com/core-specifications/
- Gurux DLMS Python: https://github.com/Gurux/Gurux.DLMS.Python
- Wireshark: https://www.wireshark.org/
- Docker Compose: https://docs.docker.com/compose/
- GitHub Copilot in VS Code: https://code.visualstudio.com/docs/copilot/overview
- Power BI Desktop: https://www.microsoft.com/en-us/power-platform/products/power-bi/downloads
- FastAPI: https://fastapi.tiangolo.com/
- pandas: https://pandas.pydata.org/

---

## 34. Checklist final de entrega

- [ ] Repositorio en GitHub.
- [ ] README completo.
- [ ] Docker Compose funcional.
- [ ] Datos sintéticos generados.
- [ ] Base PostgreSQL/PostGIS cargada.
- [ ] Cálculo de balances operativo.
- [ ] Detección de anomalías operativa.
- [ ] Publicación MQTT funcional.
- [ ] Dashboard Grafana creado.
- [ ] Mapa QGIS creado.
- [ ] Pruebas unitarias pasando.
- [ ] Capturas en `docs/screenshots`.
- [ ] Informe corto en PDF.
- [ ] Video demo.
- [ ] Versión corta para CV.
- [ ] Explicación preparada para entrevista.

---

## 35. Próximo paso recomendado

Construir primero el MVP:

```bash
docker compose up -d
python src/generate_assets.py
python src/generate_synthetic_readings.py
python src/calculate_energy_balance.py
python src/detect_anomalies.py
pytest
```

Con eso ya tendrás una primera versión defendible. Después agregas QGIS, Node-RED, MQTT, OpenDSS, PyModbus y DLMS/COSEM por fases.
