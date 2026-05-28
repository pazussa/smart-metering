# Smart Metering & Loss Analysis Lab

Laboratorio reproducible de **macromedicion, telemedicion y analisis de perdidas de energia** construido con Python, PostgreSQL/PostGIS, Grafana OSS, FastAPI, MQTT/Mosquitto, Node-RED, OpenDSS y datos sinteticos.

Este proyecto fue desarrollado como evidencia de portafolio para aplicar a cargos como **Profesional de Gestion de Perdidas**, **Profesional de Macromedicion**, **Analista de Perdidas de Energia** o roles afines en medicion inteligente, balances energeticos y gestion de informacion tecnica.

> El laboratorio no se conecta a infraestructura real. Simula una red de distribucion, genera lecturas sinteticas, calcula balances por transformador, estima perdidas, detecta alertas, publica telemetria por MQTT y expone resultados en base de datos, API, mapas y tableros.

![Resumen del laboratorio](docs/screenshots/00_demo_cover.png)

## Objetivo

Demostrar capacidades tecnicas para ejecutar actividades de cargue, validacion y analisis de informacion orientadas a:

- identificar sectores y clientes a intervenir en programas de reduccion y control de perdidas;
- calcular balances energeticos por transformador, alimentador o sector;
- analizar disponibilidad de telemedicion y lecturas faltantes;
- detectar lecturas atipicas y posibles fallas de comunicacion;
- soportar decisiones de mantenimiento, expansion de cobertura de macromedicion y medicion inteligente;
- documentar un flujo reproducible con herramientas gratuitas.

## Relacion con cargos de gestion de perdidas

Este proyecto se alinea con funciones tipicas de gestion de perdidas de energia:

| Requisito del cargo | Evidencia en el proyecto |
|---|---|
| Analisis para gestion de perdidas | Calculo de perdida kWh, perdida porcentual, ranking de transformadores criticos y alertas |
| Balances energeticos | Balance entre energia de macromedidor y suma de medidores aguas abajo |
| Estrategias de reduccion de perdidas | Identificacion de sectores con alta perdida y baja disponibilidad |
| Macromedicion directa, semidirecta, convencional o telemedida | Simulacion de macromedidores por transformador y medidores inteligentes asociados |
| Sistemas de comunicacion | MQTT/Mosquitto, Node-RED, Modbus y exploracion OpenDSS |
| Analisis de datos | Python, pandas, validacion de calidad, API y PostgreSQL/PostGIS |
| Visualizacion operativa | Graficas, mapas GIS, FastAPI Swagger y dashboard Grafana |

## Arquitectura

El flujo principal genera activos, lecturas y eventos; calcula indicadores; carga los resultados en PostgreSQL/PostGIS; y los expone mediante API, mapas, tableros y protocolos de telemedicion.

![Arquitectura](docs/screenshots/01_architecture.png)

Componentes principales:

- **Python**: generacion sintetica, calculo de balances, deteccion de alertas y pruebas.
- **PostgreSQL/PostGIS**: almacenamiento de activos, lecturas, balances, alertas y geometria.
- **FastAPI**: API REST para consultar balances y alertas.
- **Grafana OSS**: tablero operacional conectado a PostgreSQL.
- **Mosquitto MQTT**: broker para simular telemedicion.
- **Node-RED**: entorno visual para flujos de telemetria.
- **OpenDSS**: simulacion electrica basica de red de distribucion.
- **GeoJSON/QGIS**: visualizacion geografica de activos y sectores criticos.

## Resultados generados

El escenario sintetico validado genera:

- 2 alimentadores.
- 6 transformadores.
- 78 medidores, incluyendo macromedidores.
- 11.737 lecturas horarias de medidores.
- 359 eventos de comunicacion.
- 1.008 balances energeticos.
- 948 alertas operativas.
- 86 elementos GIS exportados.

![Resumen de indicadores](docs/screenshots/02_kpi_summary.png)

## Indicadores tecnicos

| Indicador | Logica |
|---|---|
| Energia suministrada | Lectura del macromedidor por transformador |
| Energia medida | Suma de lecturas de medidores aguas abajo |
| Perdida kWh | Energia suministrada - energia medida |
| Perdida % | Perdida kWh / energia suministrada * 100 |
| Disponibilidad de lecturas | Lecturas recibidas / lecturas esperadas * 100 |
| Alertas de perdida alta | Perdida porcentual mayor al umbral configurado |
| Alertas de baja disponibilidad | Disponibilidad menor al umbral configurado |
| Lecturas atipicas | Lecturas marcadas como anomalas o fuera de rango |

## Evidencias visuales

### Perdidas por transformador

La linea roja punteada representa el umbral de perdida alta. El grafico permite priorizar transformadores o sectores con comportamiento critico.

![Perdidas por transformador](docs/screenshots/03_loss_timeseries.png)

### Balance energetico reciente

Compara energia de entrada, energia medida y perdida estimada por transformador.

![Balance energetico](docs/screenshots/04_energy_balance_latest.png)

### Disponibilidad de telemedicion

La matriz muestra la disponibilidad de lecturas por transformador y ventana horaria.

![Disponibilidad](docs/screenshots/05_availability_heatmap.png)

### Ranking de sectores criticos

Ordena transformadores por perdida promedio para apoyar la priorizacion de intervenciones.

![Ranking critico](docs/screenshots/06_critical_ranking.png)

### Alertas operativas

Resume alertas por tipo y severidad: perdida alta, baja disponibilidad y lecturas atipicas.

![Alertas](docs/screenshots/07_alerts_breakdown.png)

### Mapa GIS de activos

Ubica alimentadores, transformadores, macromedidores y medidores inteligentes. El color de cada transformador representa la ultima perdida porcentual calculada.

![Mapa GIS](docs/screenshots/08_gis_assets_map.png)

### Modelo de datos

Modelo relacional usado para activos, lecturas, macromedicion, balances y alertas.

![Modelo de datos](docs/screenshots/09_data_model.png)

### Validacion ejecutada

Pruebas de servicios, base de datos, telemetria, OpenDSS, API y evidencia GIS.

![Validacion](docs/screenshots/10_validation_matrix.png)

### API REST

FastAPI expone endpoints para salud, ultimos balances y alertas abiertas.

![FastAPI Swagger](docs/screenshots/11_fastapi_swagger.png)

## Estructura del proyecto

```text
.
├── data/
│   ├── synthetic/              # datos sinteticos generados
│   └── processed/              # balances y alertas calculadas
├── dashboards/grafana/         # dashboard y provisioning de Grafana
├── docs/
│   └── screenshots/            # imagenes usadas en este README
├── maps/                       # GeoJSON para QGIS
├── mqtt/                       # configuracion de Mosquitto
├── opendss/                    # caso basico OpenDSS
├── scripts/                    # ejecucion y generacion de demo
├── sql/                        # extensiones, esquema y vistas PostGIS
├── src/                        # codigo Python del laboratorio
└── tests/                      # pruebas automatizadas
```

## Ejecucion rapida

Requisitos:

- Python 3.11 o superior.
- Docker y Docker Compose.
- Git.

Crear entorno:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ejecutar flujo local sin contenedores:

```bash
./scripts/run_local_mvp.sh
```

Levantar laboratorio completo con Docker:

```bash
./scripts/run_docker_stack.sh
```

El script:

1. valida el entorno;
2. genera activos y lecturas sinteticas;
3. calcula balances energeticos;
4. detecta alertas;
5. exporta GeoJSON;
6. levanta PostgreSQL/PostGIS, Grafana, Mosquitto, Node-RED, InfluxDB y FastAPI;
7. carga la base de datos;
8. prueba PostgreSQL, MQTT, API y pytest.

## URLs locales

Con Docker ejecutandose:

| Servicio | URL |
|---|---|
| FastAPI Swagger | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| Dashboard Grafana | http://localhost:3000/d/smart-metering-loss/smart-metering-loss-analysis |
| Node-RED | http://localhost:1880 |
| PostgreSQL/PostGIS | localhost:5432 |
| Mosquitto MQTT | localhost:1883 |

Credenciales de Grafana:

```text
usuario: admin
clave: admin
```

## Comandos utiles

Diagnostico del entorno:

```bash
python -m src.doctor --require-docker
```

Regenerar imagenes de demo:

```bash
python scripts/generate_demo_images.py
```

Ejecutar pruebas:

```bash
pytest
ruff check .
black --check src tests scripts
```

Consultar la API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/balances/latest
curl http://localhost:8000/alerts/open
```

Apagar servicios:

```bash
docker-compose down
```

## Validacion realizada

El proyecto fue probado con:

- `pytest`: 18 pruebas automatizadas.
- `ruff`: analisis estatico.
- `black --check`: formato.
- `docker-compose config`: validacion de Compose.
- Smoke test de PostgreSQL/PostGIS.
- Smoke test MQTT publish/subscribe.
- FastAPI contra PostgreSQL.
- Grafana conectado a PostgreSQL.
- Node-RED levantado.
- OpenDSS ejecutando el circuito simple.

## Nota de alcance

Los datos son sinteticos y el laboratorio no representa una certificacion oficial de perdidas. Su proposito es demostrar dominio practico en analisis de datos, macromedicion, telemedicion, visualizacion tecnica y gestion operativa de perdidas de energia.
