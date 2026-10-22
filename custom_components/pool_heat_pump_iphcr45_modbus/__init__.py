from .controller import PacController
from .const import (
    DOMAIN,
    SCAN_INTERVAL,
    CONF_SCAN_INTERVAL,
    CONF_BRAND,
    CONF_MODEL,
    CONF_HIVERNER,
)
from .modbus_handler import ModbusHandler
from .models import DEFAULT_BRAND, DEFAULT_MODEL, resolve_model

PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "select", "climate"]


async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})

    data = dict(entry.data)

    # Model chosen at configuration time (falls back to the default for entries
    # created before brand/model selection was added).
    model_config = resolve_model(
        data.get(CONF_BRAND, DEFAULT_BRAND),
        data.get(CONF_MODEL, DEFAULT_MODEL),
    )

    handler = ModbusHandler(data["host"], data["port"], data["unit_id"])

    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    )
    hivernage = bool(
        entry.options.get(CONF_HIVERNER, data.get(CONF_HIVERNER, False))
    )
    controller = PacController(
        hass, lambda now: None, scan_interval, handler, hivernage
    )

    hass.data[DOMAIN][entry.entry_id] = {
        **data,
        "model_config": model_config,
        "controller": controller,
        "scan_interval": scan_interval,
    }

    controller.start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # First poll in a background task: never during setup, never blocking if
    # the heat pump is powered off (same fix as the pool_technologie integration).
    entry.async_create_background_task(
        hass, controller.async_initial_poll(), f"{DOMAIN}_initial_poll"
    )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass, entry):
    """Apply an options change.

    A refresh interval change requires a reload; wintering is applied in
    place, because reloading the entry would remove all entities and make
    the wintering switch temporarily unreachable.
    """
    controller = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("controller")
    if controller is None:
        return

    new_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    )
    if new_interval != controller.scan_interval:
        await hass.config_entries.async_reload(entry.entry_id)
        return

    new_hivernage = bool(entry.options.get(CONF_HIVERNER, False))
    if new_hivernage != controller.hivernage:
        # Wintering changed from the options UI: applied without reloading.
        controller.set_hivernage(new_hivernage)
        controller.refresh_states()


async def async_unload_entry(hass, entry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        controller = hass.data[DOMAIN][entry.entry_id]["controller"]
        await controller.stop()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
