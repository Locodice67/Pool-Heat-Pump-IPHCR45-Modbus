"""Vérifie ModbusHandler hors ligne : `python tests/test_modbus_handler.py`."""

import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
try:  # HA installé : import normal du paquet.
    from custom_components.pool_heat_pump_iphcr45_modbus.modbus_handler import (
        COIL, DISCRETE_INPUT, HOLDING, INPUT, ModbusHandler,
    )
except ModuleNotFoundError:  # HA absent : charge uniquement le module testé.
    import importlib.util

    _path = _ROOT / "custom_components/pool_heat_pump_iphcr45_modbus/modbus_handler.py"
    _spec = importlib.util.spec_from_file_location("modbus_handler", _path)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    COIL, DISCRETE_INPUT, HOLDING, INPUT, ModbusHandler = (
        _m.COIL, _m.DISCRETE_INPUT, _m.HOLDING, _m.INPUT, _m.ModbusHandler,
    )

from modbus_connection import ModbusError


class FakeUnit:
    """Doublure async : valeurs fixes, aucune I/O."""

    def __init__(self, values=(42,), fail=False):
        self.values, self.fail, self.calls = list(values), fail, []

    def __getattr__(self, name):
        async def call(*args):
            self.calls.append((name, *args))
            if self.fail:
                raise ModbusError("boom")
            return None if name.startswith("write_") else self.values

        return call


async def main() -> None:
    handler, unit = ModbusHandler(), FakeUnit((7,))
    handler._unit = unit
    assert await handler.read(10, HOLDING) == 7
    assert await handler.read(10, INPUT) == 7
    unit.values = [True]
    assert await handler.read(10, COIL) == 1
    unit.values = [False]
    assert await handler.read(10, DISCRETE_INPUT) == 0
    unit.fail = True
    assert await handler.read(10) is None
    unit.fail, unit.calls = False, []
    assert await handler.write(10, 5) is True
    assert unit.calls[-1] == ("write_register", 10, 5)
    assert await handler.write(10, 1, COIL) is True
    assert unit.calls[-1] == ("write_coil", 10, True)
    unit.fail = True
    assert await handler.write(10, 5) is False
    unit.fail, unit.values = False, [10]
    assert await handler.read_verified(10, 12, tolerance=2) is True
    assert await handler.read_verified(10, 13, tolerance=2) is False
    unit.fail = True
    assert await handler.read_verified(10, 10) is False


if __name__ == "__main__":
    asyncio.run(main())
    print("tests/test_modbus_handler.py: OK")
