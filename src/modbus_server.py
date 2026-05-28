from __future__ import annotations

import argparse


def encode_reading_registers(
    energy_kwh: float,
    voltage_v: float,
    current_a: float,
    power_factor: float,
) -> list[int]:
    values = [
        int(round(energy_kwh * 100)),
        int(round(voltage_v * 10)),
        int(round(current_a * 100)),
        int(round(power_factor * 1000)),
    ]
    for value in values:
        if not 0 <= value <= 65535:
            raise ValueError(f"Register value out of range: {value}")
    return values


def _load_datastore_classes():
    try:
        import pymodbus.datastore as datastore
    except ImportError as exc:
        raise RuntimeError("pymodbus is required for the Modbus server") from exc

    device_context = getattr(
        datastore,
        "ModbusDeviceContext",
        getattr(datastore, "ModbusSlaveContext", None),
    )
    if device_context is None:
        raise RuntimeError("Unsupported pymodbus datastore API")

    return datastore.ModbusSequentialDataBlock, datastore.ModbusServerContext, device_context


def build_server_context(registers: list[int]):
    data_block, server_context, device_context = _load_datastore_classes()

    device = device_context(hr=data_block(1, registers))
    return server_context(devices=device, single=True)


def run_server(
    host: str = "127.0.0.1",
    port: int = 5020,
    registers: list[int] | None = None,
) -> None:
    try:
        from pymodbus.server import StartTcpServer
    except ImportError as exc:
        raise RuntimeError("pymodbus is required for the Modbus server") from exc

    holding_registers = registers or encode_reading_registers(125.34, 120.1, 10.42, 0.94)
    context = build_server_context(holding_registers)
    print(f"Starting Modbus TCP server on {host}:{port} with HR={holding_registers}")
    StartTcpServer(context=context, address=(host, port))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a synthetic Modbus TCP server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5020)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
