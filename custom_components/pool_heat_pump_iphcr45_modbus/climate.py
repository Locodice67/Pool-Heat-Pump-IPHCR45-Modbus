import asyncio
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import DOMAIN
from .entity import PacDeviceMixin

_LOGGER = logging.getLogger(__name__)

# Option (model key) -> Home Assistant HVACMode
_HVAC_OPTION_TO_MODE = {
    "auto": HVACMode.AUTO,
    "heat": HVACMode.HEAT,
    "cool": HVACMode.COOL,
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    controller = entry_data["controller"]
    handler = controller.handler

    async_add_entities(
        [
            PacThermostat(
                hass,
                handler,
                controller,
                config_entry.entry_id,
                entry_data["model_config"]["climate"],
            )
        ]
    )


class PacThermostat(PacDeviceMixin, ClimateEntity):
    """Heat pump thermostat: setpoint, heating mode and fan mode."""

    _attr_should_poll = False
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:heat-pump"

    def __init__(self, hass, handler, controller, entry_id, config):
        self._hass = hass
        self._handler = handler
        self._controller = controller
        self._entry_id = entry_id
        self._config = config

        self._attr_has_entity_name = True
        self._attr_translation_key = config["translation_key"]
        self._attr_unique_id = f"{entry_id}_{config['unique_id']}"

        target = config["target_temperature"]
        self._attr_min_temp = target["min"]
        self._attr_max_temp = target["max"]
        self._attr_target_temperature_step = target["step"]

        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.COOL]
        self._attr_fan_modes = list(config["fan_mode"]["values"].keys())
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
        )

        self._raw_to_hvac = {
            raw: option for option, raw in config["hvac_mode"]["values"].items()
        }
        self._raw_to_fan = {
            raw: option for option, raw in config["fan_mode"]["values"].items()
        }

        self._attr_current_temperature = None
        self._attr_target_temperature = None
        self._attr_hvac_mode = None
        self._attr_fan_mode = None

    @property
    def extra_state_attributes(self):
        return {
            "modbus_current_temperature": self._config["current_temperature"]["address"],
            "modbus_target_temperature": self._config["target_temperature"]["address"],
            "modbus_hvac_mode": self._config["hvac_mode"]["address"],
            "modbus_fan_mode": self._config["fan_mode"]["address"],
        }

    async def async_added_to_hass(self):
        self._controller.add_poll_listener(self._async_poll_refresh)
        self._controller.add_state_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._controller.remove_poll_listener(self._async_poll_refresh)

    def _to_value(self, raw, spec):
        return round(
            raw * spec.get("scale", 1) + spec.get("offset", 0),
            spec.get("precision", 0),
        )

    def _to_raw(self, value, spec):
        scale = spec.get("scale", 1) or 1
        return int(round((value - spec.get("offset", 0)) / scale))

    async def _read(self, spec):
        return await self._handler.read(spec["address"], spec["input_type"])

    async def _write(self, spec, raw) -> bool:
        ok = await self._handler.write(spec["address"], raw, spec["input_type"])
        if not ok:
            _LOGGER.warning("Modbus write failed at %s", spec["address"])
            return False

        await asyncio.sleep(0.5)
        verified = await self._handler.read_verified(
            spec["address"],
            raw,
            spec["input_type"],
            0,
        )
        if not verified:
            _LOGGER.warning(
                "Write not confirmed by the device (register %s)", spec["address"]
            )
            return False
        return True

    async def _async_poll_refresh(self) -> bool:
        any_success = False

        raw_current = await self._read(self._config["current_temperature"])
        if raw_current is not None:
            self._attr_current_temperature = self._to_value(
                raw_current, self._config["current_temperature"]
            )
            any_success = True

        raw_target = await self._read(self._config["target_temperature"])
        if raw_target is not None:
            self._attr_target_temperature = self._to_value(
                raw_target, self._config["target_temperature"]
            )
            any_success = True

        raw_hvac = await self._read(self._config["hvac_mode"])
        if raw_hvac is not None:
            option = self._raw_to_hvac.get(raw_hvac)
            if option is not None:
                self._attr_hvac_mode = _HVAC_OPTION_TO_MODE.get(option, option)
            any_success = True

        raw_fan = await self._read(self._config["fan_mode"])
        if raw_fan is not None:
            fan = self._raw_to_fan.get(raw_fan)
            if fan is not None:
                self._attr_fan_mode = fan
            any_success = True

        self.async_write_ha_state()
        return any_success

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        spec = self._config["target_temperature"]
        raw = self._to_raw(temperature, spec)
        if await self._write(spec, raw):
            self._attr_target_temperature = temperature
            self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        spec = self._config["hvac_mode"]
        for option, mode in _HVAC_OPTION_TO_MODE.items():
            if mode == hvac_mode:
                raw = spec["values"].get(option)
                if raw is None:
                    return
                if await self._write(spec, raw):
                    self._attr_hvac_mode = hvac_mode
                    self.async_write_ha_state()
                return

    async def async_set_fan_mode(self, fan_mode):
        spec = self._config["fan_mode"]
        raw = spec["values"].get(fan_mode)
        if raw is None:
            return
        if await self._write(spec, raw):
            self._attr_fan_mode = fan_mode
            self.async_write_ha_state()
