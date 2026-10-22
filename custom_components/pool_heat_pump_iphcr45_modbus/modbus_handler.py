import logging

from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

_LOGGER = logging.getLogger(__name__)

COIL = "coil"
DISCRETE_INPUT = "discrete_input"
INPUT = "input"
HOLDING = "holding"


class ModbusHandler:
    """Connexion Modbus TCP asynchrone vers la passerelle de la PAC.

    `modbus_connection` (backend tmodbus) gère la liaison de bout en bout :
    chaque lecture/écriture ouvre la connexion à la demande, la réouvre après
    une coupure et lève une sous-classe de `ModbusError` en cas d'échec. Les
    méthodes sont donc natives asyncio et s'appellent directement depuis la
    boucle d'événements de Home Assistant, sans passer par un thread. La même
    instance est partagée par toutes les plateformes de l'intégration.
    """

    def __init__(self, host="192.168.1.100", port=502, unit_id=1, timeout=3):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        # Aucune I/O dans le constructeur : la liaison s'ouvre au premier usage.
        self._connection = ModbusConnection(
            ModbusTcpParams(host=host, port=port), timeout=timeout
        )
        self._unit = self._connection.for_unit(unit_id)
        self._unit.require_timeout(timeout)

    async def connect(self) -> bool:
        """Ouvre la connexion. Peut être appelé plusieurs fois."""
        try:
            await self._connection.connect()
            return True
        except ModbusError as err:
            _LOGGER.debug(
                "Connexion Modbus impossible (%s:%s) : %s", self.host, self.port, err
            )
            return False

    async def close(self) -> None:
        await self._connection.close()

    async def reconnect(self) -> None:
        """Recycle la liaison : la prochaine requête se reconnectera d'elle-même."""
        try:
            await self._connection.disconnect()
        except ModbusError as err:
            # Déconnexion impossible : sans gravité, la prochaine requête
            # rouvrira la liaison à la demande.
            _LOGGER.debug("Reconnexion Modbus impossible : %s", err)

    async def read(self, address, input_type=HOLDING, count=1):
        """Lit `count` valeurs et renvoie la première, ou None en cas d'échec."""
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
                "Erreur de lecture Modbus à %s (%s) : %s", address, input_type, err
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
                "Erreur d'écriture Modbus à %s (%s) : %s", address, input_type, err
            )
            return False

    async def read_verified(
        self, address, expected_value, input_type=HOLDING, tolerance=0
    ):
        """Relit une valeur après une écriture pour confirmer qu'elle est appliquée.

        À appeler après write(), avec un court délai si l'appareil a besoin de
        temps pour traiter.
        """
        result = await self.read(address, input_type=input_type)
        if result is None:
            return False
        return abs(result - expected_value) <= tolerance
