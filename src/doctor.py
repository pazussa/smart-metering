from __future__ import annotations

import argparse
import importlib
import shutil
import subprocess
import sys
from dataclasses import dataclass

from src.config import BASE_DIR


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    required: bool = True


REQUIRED_FILES = [
    "docker-compose.yml",
    "Dockerfile.api",
    "requirements.txt",
    "requirements-api.txt",
    "sql/01_extensions.sql",
    "sql/02_schema.sql",
    "sql/03_views.sql",
    "mqtt/mosquitto.conf",
    "dashboards/grafana/smart-metering-loss-dashboard.json",
]

GENERATED_FILES = [
    "data/synthetic/feeders.csv",
    "data/synthetic/transformers.csv",
    "data/synthetic/meters.csv",
    "data/synthetic/readings.csv",
    "data/synthetic/macro_readings.csv",
    "data/synthetic/communication_events.csv",
    "data/processed/energy_balance.csv",
    "data/processed/alerts.csv",
    "maps/assets.geojson",
]

REQUIRED_MODULES = [
    "pandas",
    "numpy",
    "sqlalchemy",
    "psycopg2",
    "fastapi",
    "paho.mqtt.client",
    "pymodbus",
    "opendssdirect",
]


def run_command(command: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=BASE_DIR,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, f"Command not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"Command timed out: {' '.join(command)}"
    return completed.returncode, completed.stdout.strip()


def find_compose_command() -> list[str] | None:
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    if shutil.which("docker"):
        code, _ = run_command(["docker", "compose", "version"], timeout=10)
        if code == 0:
            return ["docker", "compose"]
    return None


def check_python() -> CheckResult:
    version = sys.version_info
    ok = version >= (3, 11)
    detail = f"{version.major}.{version.minor}.{version.micro}"
    return CheckResult("Python >= 3.11", ok, detail)


def check_modules() -> CheckResult:
    missing = []
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(module_name)
    if missing:
        return CheckResult("Python dependencies", False, f"Missing: {', '.join(missing)}")
    return CheckResult("Python dependencies", True, "All required modules import")


def check_files(files: list[str], name: str, required: bool = True) -> CheckResult:
    missing = [file for file in files if not (BASE_DIR / file).exists()]
    if missing:
        return CheckResult(name, False, f"Missing: {', '.join(missing)}", required=required)
    return CheckResult(name, True, f"{len(files)} files present", required=required)


def check_docker_cli() -> CheckResult:
    docker = shutil.which("docker")
    if not docker:
        return CheckResult("Docker CLI", False, "docker command not found")
    return CheckResult("Docker CLI", True, docker)


def check_compose_config() -> CheckResult:
    compose = find_compose_command()
    if not compose:
        return CheckResult("Docker Compose", False, "docker-compose or docker compose not found")
    code, output = run_command([*compose, "config"], timeout=30)
    if code != 0:
        return CheckResult("Docker Compose config", False, output)
    return CheckResult("Docker Compose config", True, "Compose file is valid")


def check_docker_daemon(required: bool = False) -> CheckResult:
    if not shutil.which("docker"):
        return CheckResult("Docker daemon", False, "docker command not found", required=required)
    code, output = run_command(["docker", "info"], timeout=20)
    if code == 0:
        return CheckResult("Docker daemon", True, "Docker daemon is reachable", required=required)

    status_code, status = run_command(["systemctl", "is-active", "docker"], timeout=5)
    masked_code, masked = run_command(["systemctl", "is-enabled", "docker"], timeout=5)
    hints = [output.splitlines()[-1] if output else "docker info failed"]
    if status_code == 0 or status:
        hints.append(f"systemctl is-active docker: {status}")
    if masked_code == 0 or masked:
        hints.append(f"systemctl is-enabled docker: {masked}")
    hints.append("Start Docker before running the container stack")
    return CheckResult("Docker daemon", False, " | ".join(hints), required=required)


def collect_checks(require_docker: bool = False) -> list[CheckResult]:
    return [
        check_python(),
        check_modules(),
        check_files(REQUIRED_FILES, "Project files"),
        check_files(GENERATED_FILES, "Generated lab data", required=False),
        check_docker_cli(),
        check_compose_config(),
        check_docker_daemon(required=require_docker),
    ]


def print_report(results: list[CheckResult]) -> None:
    for result in results:
        marker = "OK" if result.ok else ("FAIL" if result.required else "WARN")
        print(f"[{marker}] {result.name}: {result.detail}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local smart-metering lab readiness.")
    parser.add_argument(
        "--require-docker",
        action="store_true",
        help="Exit non-zero if the Docker daemon is not reachable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = collect_checks(require_docker=args.require_docker)
    print_report(results)
    failed_required = [result for result in results if result.required and not result.ok]
    raise SystemExit(1 if failed_required else 0)


if __name__ == "__main__":
    main()
