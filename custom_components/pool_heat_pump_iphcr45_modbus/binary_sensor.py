from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .entity import PacDeviceMixin


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    controller = entry_data["controller"]
    handler = controller.handler
    entry_id = config_entry.entry_id

    entities = [ModbusStatusSensor(entry_id, controller)]
    entities.extend(
        PacRegisterBinarySensor(conf, hass, handler, controller, entry_id)
        for conf in entry_data["model_config"]["binary_sensors"]
    )
    async_add_entities(entities)


class ModbusStatusSensor(PacDeviceMixin, BinarySensorEntity):
    """État local de la liaison Modbus (diagnostic), pas une I/O de l'appareil."""

    def __init__(self, entry_id, controller):
        self._entry_id = entry_id
        self._controller = controller

        self._attr_has_entity_name = True
        self._attr_translation_key = "modbus_status"
        self._attr_unique_id = f"{entry_id}_modbus_status"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:lan-connect"
        self._attr_is_on = controller.modbus_ok

    @property
    def is_on(self):
        return self._controller.modbus_ok

    async def async_added_to_hass(self):
        self._controller.add_state_listener(self.async_write_ha_state)

    async def async_update(self):
        self._attr_is_on = self._controller.modbus_ok


class PacRegisterBinarySensor(PacDeviceMixin, BinarySensorEntity):
    """Binary sensor dérivé d'une bobine ou d'une entrée TOR Modbus."""

    _attr_should_poll = False

    def __init__(self, config, hass, handler, controller, entry_id):
        self._config = config
        self._hass = hass
        self._handler = handler
        self._controller = controller
        self._entry_id = entry_id
        self._address = config["address"]
        self._input_type = config["input_type"]

        self._attr_has_entity_name = True
        self._attr_translation_key = config["translation_key"]
        self._attr_unique_id = f"{entry_id}_{config['unique_id']}"
        self._attr_icon = config.get("icon")
        if config.get("device_class") == "problem":
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_is_on = False

    @property
    def extra_state_attributes(self):
        return {"modbus_address": self._address, "modbus_type": self._input_type}

    async def async_added_to_hass(self):
        self._controller.add_poll_listener(self._async_poll_refresh)
        self._controller.add_state_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._controller.remove_poll_listener(self._async_poll_refresh)

    async def _async_poll_refresh(self) -> bool:
        raw = await self._handler.read(self._address, self._input_type)
        if raw is None:
            return False
        self._attr_is_on = bool(raw)
        self.async_write_ha_state()
        return True
