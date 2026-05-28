from __future__ import annotations

import argparse


def decode_reading_registers(registers: list[int]) -> dict[str, float]:
    if len(registers) < 4:
        raise ValueError("At least four holding registers are required")
    return {
        "energy_kwh": registers[0] / 100,
        "voltage_v": registers[1] / 10,
        "current_a": registers[2] / 100,
        "power_factor": registers[3] / 1000,
    }


def read_registers(host: str = "127.0.0.1", port: int = 5020, address: int = 0) -> dict[str, float]:
    try:
        from pymodbus.client import ModbusTcpClient
    except ImportError as exc:
        raise RuntimeError("pymodbus is required for the Modbus client") from exc

    client = ModbusTcpClient(host=host, port=port)
    try:
        if not client.connect():
            raise ConnectionError(f"Could not connect to Modbus server at {host}:{port}")
        response = client.read_holding_registers(address=address, count=4)
        if response.isError():
            raise RuntimeError(f"Modbus error response: {response}")
        return decode_reading_registers(list(response.registers))
    finally:
        client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read synthetic Modbus registers.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5020)
    parser.add_argument("--address", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(read_registers(args.host, args.port, args.address))


if __name__ == "__main__":
    main()
