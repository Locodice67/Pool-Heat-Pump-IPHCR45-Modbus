import logging

from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

_LOGGER = logging.getLogger(__name__)

COIL = "coil"
DISCRETE_INPUT = "discrete_input"
INPUT = "input"
HOLDING = "holding"


class ModbusHandler:
    """Asynchronous Modbus TCP connection to the heat pump gateway.

    `modbus_connection` (tmodbus backend) handles the link end to end:
    each read/write opens the connection on demand, reopens it after a
    drop and raises a `ModbusError` subclass on failure. The methods are
    therefore native asyncio and are called directly from the Home
    Assistant event loop, without going through a thread. The same
    instance is shared by all platforms of the integration.
    """

    def __init__(self, host="192.168.1.100", port=502, unit_id=1, timeout=3):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        # No I/O in the constructor: the link opens on first use.
        self._connection = ModbusConnection(
            ModbusTcpParams(host=host, port=port), timeout=timeout
        )
        self._unit = self._connection.for_unit(unit_id)
        self._unit.require_timeout(timeout)

    async def connect(self) -> bool:
        """Open the connection. May be called several times."""
        try:
            await self._connection.connect()
            return True
        except ModbusError as err:
            _LOGGER.debug(
                "Modbus connection failed (%s:%s): %s", self.host, self.port, err
            )
            return False

    async def close(self) -> None:
        await self._connection.close()

    async def reconnect(self) -> None:
        """Recycle the link: the next request reconnects on its own."""
        try:
            await self._connection.disconnect()
        except ModbusError as err:
            # Disconnect failed: harmless, the next request
            # reopens the link on demand.
            _LOGGER.debug("Modbus reconnect failed: %s", err)

    async def read(self, address, input_type=HOLDING, count=1):
        """Read `count` values and return the first, or None on failure."""
        try:
            if input_type == COIL:
                values = await self._unit.read_coils(address, count)
            elif input_type == DISCRETE_INPUT:
                values = await self._unit.read_discrete_inputs(address, count)
            elif input_type == INPUT:
                values = await self._unit.read_input_registers(address, count)
            else:
                values = await self._unit.read_holding_registers(address, count)

            if input_type in (COIL, DISCRETE_INPUT):
                return 1 if values[0] else 0
            return values[0]
        except ModbusError as err:
            _LOGGER.debug(
                "Modbus read error at %s (%s): %s", address, input_type, err
            )
            return None

    async def write(self, address, value, input_type=HOLDING):
        try:
            if input_type == COIL:
                await self._unit.write_coil(address, bool(value))
            else:
                await self._unit.write_register(address, int(value))
            return True
        except ModbusError as err:
            _LOGGER.debug(
                "Modbus write error at %s (%s): %s", address, input_type, err
            )
            return False

    async def read_verified(
        self, address, expected_value, input_type=HOLDING, tolerance=0
    ):
        """Re-read a value after a write to confirm it was applied.

        Call after write(), with a short delay if the device needs
        time to process.
        """
        result = await self.read(address, input_type=input_type)
        if result is None:
            return False
        return abs(result - expected_value) <= tolerance
