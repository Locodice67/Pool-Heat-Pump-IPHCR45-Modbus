import asyncio
import logging

from homeassistant.components.select import SelectEntity

from .const import DOMAIN
from .entity import PacDeviceMixin

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    controller = entry_data["controller"]
    handler = controller.handler

    async_add_entities(
        [
            PacRegisterSelect(hass, handler, controller, config_entry.entry_id, conf)
            for conf in entry_data["model_config"]["selects"]
        ]
    )


class PacRegisterSelect(PacDeviceMixin, SelectEntity):
    """Select backed by a register: options -> raw value."""

    _attr_should_poll = False

    def __init__(self, hass, handler, controller, entry_id, config):
        self._hass = hass
        self._handler = handler
        self._controller = controller
        self._entry_id = entry_id
        self._config = config
        self._option_to_raw = dict(config["options"])
        self._raw_to_option = {raw: option for option, raw in config["options"].items()}

        self._attr_has_entity_name = True
        self._attr_translation_key = config["translation_key"]
        self._attr_unique_id = f"{entry_id}_{config['unique_id']}"
        self._attr_icon = config.get("icon")
        self._attr_options = list(config["options"].keys())
        self._attr_current_option = None

    @property
    def extra_state_attributes(self):
        return {"modbus_address": self._config["address"]}

    async def async_added_to_hass(self):
        self._controller.add_poll_listener(self._async_poll_refresh)
        self._controller.add_state_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._controller.remove_poll_listener(self._async_poll_refresh)

    async def _async_poll_refresh(self) -> bool:
        raw = await self._handler.read(
            self._config["address"], self._config["input_type"]
        )
        if raw is None:
            return False

        option = self._raw_to_option.get(raw)
        if option is None:
            return False

        self._attr_current_option = option
        self.async_write_ha_state()
        return True

    async def async_select_option(self, option: str) -> None:
        raw = self._option_to_raw.get(option)
        if raw is None:
            return

        ok = await self._handler.write(
            self._config["address"], raw, self._config["input_type"]
        )
        if not ok:
            _LOGGER.warning(
                "Failed to write %s (%s)", self._config["unique_id"], option
            )
            return

        await asyncio.sleep(0.5)
        verified = await self._handler.read_verified(
            self._config["address"],
            raw,
            self._config["input_type"],
            0,
        )
        if not verified:
            _LOGGER.warning("Selection not confirmed by the device (%s)", option)
            return

        self._attr_current_option = option
        self.async_write_ha_state()
