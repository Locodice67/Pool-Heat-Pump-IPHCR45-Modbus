import asyncio
import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity

from .const import DOMAIN
from .entity import PacDeviceMixin

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    controller = entry_data["controller"]
    handler = controller.handler

    async_add_entities(
        [
            PacSetpointNumber(
                hass,
                handler,
                controller,
                config_entry.entry_id,
                entry_data["model_config"]["number"],
            )
        ]
    )


class PacSetpointNumber(PacDeviceMixin, NumberEntity):
    _attr_should_poll = False

    def __init__(self, hass, handler, controller, entry_id, config):
        self._hass = hass
        self._handler = handler
        self._controller = controller
        self._entry_id = entry_id
        self._config = config

        self._attr_has_entity_name = True
        self._attr_translation_key = config["translation_key"]
        self._attr_unique_id = f"{entry_id}_{config['unique_id']}"
        self._attr_icon = config.get("icon")
        self._attr_native_unit_of_measurement = config.get("unit")
        self._attr_native_min_value = config["min"]
        self._attr_native_max_value = config["max"]
        self._attr_native_step = config["step"]
        self._attr_mode = "box"
        self._attr_native_value = None
        if config.get("device_class") == "temperature":
            self._attr_device_class = NumberDeviceClass.TEMPERATURE

    @property
    def extra_state_attributes(self):
        return {"modbus_address": self._config["address"]}

    async def async_added_to_hass(self):
        self._controller.add_poll_listener(self._async_poll_refresh)
        self._controller.add_state_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._controller.remove_poll_listener(self._async_poll_refresh)

    def _raw_to_value(self, raw):
        return round(
            raw * self._config.get("scale", 1) + self._config.get("offset", 0),
            self._config.get("precision", 0),
        )

    def _value_to_raw(self, value):
        scale = self._config.get("scale", 1) or 1
        return int(round((value - self._config.get("offset", 0)) / scale))

    async def _async_poll_refresh(self) -> bool:
        raw = await self._handler.read(
            self._config["address"], self._config["input_type"]
        )
        if raw is None:
            return False

        value = self._raw_to_value(raw)
        # Value out of range (device off or aberrant reading): ignore it and
        # keep the last known value rather than display nonsense.
        if not (self._config["min"] <= value <= self._config["max"]):
            return False

        self._attr_native_value = value
        self.async_write_ha_state()
        return True

    async def async_set_native_value(self, value: float) -> None:
        raw = self._value_to_raw(value)
        ok = await self._handler.write(
            self._config["address"], raw, self._config["input_type"]
        )
        if not ok:
            _LOGGER.warning("Failed to write the temperature setpoint (%s)", value)
            return

        await asyncio.sleep(0.5)
        verified = await self._handler.read_verified(
            self._config["address"],
            raw,
            self._config["input_type"],
            0,
        )
        if not verified:
            _LOGGER.warning(
                "Temperature setpoint not confirmed by the device (%s)", value
            )
            return

        self._attr_native_value = value
        self.async_write_ha_state()
