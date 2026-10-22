import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .entity import PacDeviceMixin

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    controller = entry_data["controller"]
    handler = controller.handler  # même connexion que les autres plateformes

    sensors = [
        PacSensor(sensor_conf, handler, controller, config_entry.entry_id)
        for sensor_conf in entry_data["model_config"]["sensors"]
    ]
    async_add_entities(sensors)

    async def update_sensors(now):
        if controller.should_skip_poll():
            return
        any_success = False
        for sensor in sensors:
            # Lecture asynchrone : l'attente rend la main à la boucle HA
            # pendant le timeout Modbus éventuel.
            ok = await sensor.update()
            if ok:
                any_success = True
            sensor.async_write_ha_state()
        # Rafraîchit les entités des autres plateformes (switch, number, select,
        # climate, binary_sensor) sur le même cycle de poll.
        for poll_listener in list(controller._poll_listeners):
            if await poll_listener():
                any_success = True
        # Un seul appel par cycle : une lecture isolée en échec ne doit pas, à
        # elle seule, faire avancer le compteur de déconnexion si d'autres
        # lectures du même cycle ont réussi.
        if any_success:
            controller.notify_modbus_success()
        else:
            controller.notify_modbus_failure()

    controller._update_callback = update_sensors


class PacSensor(PacDeviceMixin, SensorEntity, RestoreEntity):
    # Le rafraîchissement est piloté par le controller, pas par HA : pas besoin
    # que HA nous appelle aussi.
    _attr_should_poll = False

    def __init__(self, config, handler, controller, entry_id):
        self._config = config
        self._handler = handler
        self._controller = controller
        self._entry_id = entry_id
        self._state = None

        self._attr_translation_key = config["translation_key"]
        self._attr_has_entity_name = True
        self._attr_icon = config.get("icon")
        self._attr_native_unit_of_measurement = config.get("unit")
        self._attr_unique_id = f"{entry_id}_{config['unique_id']}"
        self._attr_device_class = config.get("device_class")
        if config.get("state_class"):
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "modbus_address": self._config["address"],
            "modbus_type": self._config["input_type"],
        }

    async def async_added_to_hass(self):
        self._controller.add_state_listener(self.async_write_ha_state)
        last_state = await self.async_get_last_state()
        if last_state and self._state is None:
            try:
                self._state = float(last_state.state)
            except (ValueError, TypeError):
                pass

    async def update(self) -> bool:
        """Lit la valeur du capteur, directement dans la boucle asyncio.

        Retourne True/False ; c'est update_sensors() qui décide, une fois par
        cycle, d'appeler controller.notify_modbus_success/failure.
        """
        raw = await self._handler.read(
            self._config["address"], self._config["input_type"]
        )
        if raw is None:
            return False

        value = round(
            raw * self._config.get("scale", 1) + self._config.get("offset", 0),
            self._config.get("precision", 0),
        )

        min_valid = self._config.get("min_valid")
        max_valid = self._config.get("max_valid")
        if (min_valid is not None and value < min_valid) or (
            max_valid is not None and value > max_valid
        ):
            _LOGGER.debug(
                "Lecture hors plage ignorée pour %s : %s",
                self._config["unique_id"],
                value,
            )
            return False

        self._state = value
        return True
