import asyncio
import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN, CONF_HIVERNER
from .entity import PacDeviceMixin

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    controller = entry_data["controller"]
    handler = controller.handler

    async_add_entities(
        [
            PacSwitch(
                hass,
                handler,
                controller,
                config_entry.entry_id,
                entry_data["model_config"]["switch"],
            ),
            PacHivernageSwitch(hass, config_entry, controller, config_entry.entry_id),
        ]
    )


class PacSwitch(PacDeviceMixin, SwitchEntity):
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
        self._attr_icon = "mdi:power"
        self._attr_is_on = False

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
        self._attr_is_on = raw == self._config["on_value"]
        self.async_write_ha_state()
        return True

    async def async_turn_on(self, **kwargs):
        await self._write(self._config["on_value"], True)

    async def async_turn_off(self, **kwargs):
        await self._write(self._config["off_value"], False)

    async def _write(self, value, expected_on):
        ok = await self._handler.write(
            self._config["address"],
            value,
            self._config["input_type"],
        )
        if not ok:
            _LOGGER.warning("Failed to write the heat pump on/off state (%s)", value)
            return

        await asyncio.sleep(0.5)
        verified = await self._handler.read_verified(
            self._config["address"],
            value,
            self._config["input_type"],
            0,
        )
        if not verified:
            _LOGGER.warning("Heat pump command not confirmed by the device (%s)", value)
            return

        self._attr_is_on = expected_on
        self.async_write_ha_state()


class PacHivernageSwitch(PacDeviceMixin, SwitchEntity):
    """Set the heat pump to wintering: no more Modbus I/O, entities unavailable.

    The state is stored in the config entry options; the change reloads the
    integration, so entities are recreated and become `unavailable`
    (wintering) or report their values again (wake-up).
    """

    _attr_should_poll = False
    _attr_icon = "mdi:snowflake"

    def __init__(self, hass, entry, controller, entry_id):
        self._hass = hass
        self._entry = entry
        self._controller = controller
        self._entry_id = entry_id

        self._attr_has_entity_name = True
        self._attr_translation_key = "hivernage"
        self._attr_unique_id = f"{entry_id}_hivernage"

    @property
    def is_on(self) -> bool:
        return bool(self._entry.options.get(CONF_HIVERNER, False))

    @property
    def available(self) -> bool:
        """Always available: it is the only way out of wintering."""
        return True

    async def async_turn_on(self, **kwargs) -> None:
        self._set(True)

    async def async_turn_off(self, **kwargs) -> None:
        self._set(False)

    def _set(self, enabled: bool) -> None:
        # Immediate effect (no more I/O), then persist the choice: the update
        # listener only reloads if the refresh interval changes.
        self._controller.set_hivernage(enabled)
        self._hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, CONF_HIVERNER: enabled},
        )
        self.async_write_ha_state()
        # Rewrite entity state (available) without recreating them, without
        # probing them and without any Modbus I/O.
        self._controller.refresh_states()
        if not enabled:
            # Immediate wake-up: reconnect without waiting for the next cycle.
            self._entry.async_create_background_task(
                self._hass,
                self._controller.async_initial_poll(),
                f"{DOMAIN}_hivernage_release",
            )
