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

    # Modèle choisi à la configuration (repli sur le défaut pour les entrées
    # créées avant l'ajout de la sélection marque/modèle).
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

    # Premier poll en tâche de fond : jamais pendant le setup, jamais bloquant si
    # la PAC est hors tension (même correctif que l'intégration pool_technologie).
    entry.async_create_background_task(
        hass, controller.async_initial_poll(), f"{DOMAIN}_initial_poll"
    )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass, entry):
    """Applique un changement d'options.

    L'intervalle de rafraîchissement impose un rechargement ; l'hivernage est
    appliqué en place, car recharger l'entrée retirerait toutes les entités et
    rendrait le switch d'hivernage momentanément intouchable.
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
        # Hivernage modifié depuis l'UI des options : appliqué sans recharger.
        controller.set_hivernage(new_hivernage)
        controller.refresh_states()


async def async_unload_entry(hass, entry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        controller = hass.data[DOMAIN][entry.entry_id]["controller"]
        await controller.stop()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
