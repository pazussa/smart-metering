from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.config import OPENDSS_DIR

DSS_FILE = OPENDSS_DIR / "master.dss"


def run_opendss(dss_file: str | Path = DSS_FILE, allow_missing: bool = True) -> dict[str, Any]:
    try:
        import opendssdirect as dss
    except ImportError as exc:
        if allow_missing:
            return {
                "status": "skipped",
                "reason": "opendssdirect.py is not installed",
                "dss_file": str(dss_file),
            }
        raise RuntimeError("opendssdirect.py is required to run OpenDSS") from exc

    dss_path = Path(dss_file)
    if not dss_path.exists():
        raise FileNotFoundError(dss_path)

    dss.Text.Command("Clear")
    dss.Text.Command(f"Redirect {dss_path}")
    dss.Solution.Solve()
    return {
        "status": "ok" if dss.Solution.Converged() else "not_converged",
        "circuit": dss.Circuit.Name(),
        "total_power": list(dss.Circuit.TotalPower()),
        "bus_names": list(dss.Circuit.AllBusNames()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenDSS synthetic feeder model.")
    parser.add_argument("--dss-file", default=str(DSS_FILE))
    parser.add_argument("--strict", action="store_true", help="Fail if OpenDSSDirect is missing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_opendss(args.dss_file, allow_missing=not args.strict)
    print(result)


if __name__ == "__main__":
    main()
