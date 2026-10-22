import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_UNIT_ID,
    CONF_SCAN_INTERVAL,
    CONF_BRAND,
    CONF_MODEL,
    CONF_HIVERNER,
    DEFAULT_PORT,
    SCAN_INTERVAL,
)
from .models import DEFAULT_BRAND, DEFAULT_MODEL


class PoolHeatPumpIphcr45ModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Single-step configuration: Modbus connection."""

    VERSION = 1

    def __init__(self):
        # Brand and model are no longer requested: the default is stored,
        # which leaves the rest of the code untouched (register set resolution).
        self._brand = DEFAULT_BRAND
        self._model = DEFAULT_MODEL

    # --- Single step: connection parameters -------------------------------
    async def async_step_user(self, user_input=None):
        return await self.async_step_connection(user_input)

    async def async_step_connection(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_UNIT_ID]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="PAC Piscine",
                data={
                    CONF_BRAND: self._brand,
                    CONF_MODEL: self._model,
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_UNIT_ID: user_input[CONF_UNIT_ID],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_UNIT_ID, default=1): int,
                vol.Required(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): int,
            }
        )
        return self.async_show_form(step_id="connection", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PoolHeatPumpIphcr45ModbusOptionsFlow()


class PoolHeatPumpIphcr45ModbusOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = self.config_entry
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=entry.options.get(
                        CONF_SCAN_INTERVAL,
                        entry.data.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL),
                    ),
                ): int,
                vol.Required(
                    CONF_HIVERNER,
                    default=entry.options.get(CONF_HIVERNER, False),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
