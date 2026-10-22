# Register map for the Geco heat pump (IPHCR45 and close controllers in the
# Geco/AES/Madimack series). Addresses come from a community reverse
# engineering project; re-verify on the unit before production use.
#
# Register types:
#   input           -> input register   (FC04)
#   holding         -> holding register (FC03 read / FC06 write)
#   coil            -> coil             (FC01 read / FC05 write)
#   discrete_input  -> digital input    (FC02 read only)

DEVICE_NAME = "PAC Piscine"
MANUFACTURER = "Geco"
MODEL = "GEPAC08 (Modbus)"

# Analog sensors (input registers). value = raw * scale + offset
SENSORS = [
    {
        "translation_key": "temperature_eau",
        "unique_id": "temperature_eau",
        "address": 4,
        "input_type": "input",
        "scale": 0.5,
        "offset": -30,
        "precision": 1,
        "unit": "°C",
        "icon": "mdi:thermometer-water",
        "device_class": "temperature",
        "state_class": "measurement",
        "min_valid": -10,
        "max_valid": 60,
    },
    {
        "translation_key": "temperature_air",
        "unique_id": "temperature_air",
        "address": 5,
        "input_type": "input",
        "scale": 0.5,
        "offset": -30,
        "precision": 1,
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
        "min_valid": -20,
        "max_valid": 60,
    },
    {
        "translation_key": "intensite_compresseur",
        "unique_id": "intensite_compresseur",
        "address": 11,
        "input_type": "input",
        "scale": 0.1,
        "offset": 0,
        "precision": 2,
        "unit": "A",
        "icon": "mdi:current-ac",
        "device_class": "current",
        "state_class": "measurement",
        "min_valid": 0,
        "max_valid": 10,
    },
    {
        "translation_key": "tension_pfc",
        "unique_id": "tension_pfc",
        "address": 2,
        "input_type": "input",
        "scale": 1,
        "offset": 0,
        "precision": 0,
        "unit": "V",
        "icon": "mdi:sine-wave",
        "device_class": "voltage",
        "state_class": "measurement",
        "min_valid": 0,
        "max_valid": 600,
    },
    {
        "translation_key": "compresseur",
        "unique_id": "compresseur",
        "address": 0,
        "input_type": "input",
        "scale": 1,
        "offset": 0,
        "precision": 0,
        "unit": "%",
        "icon": "mdi:gauge",
        "state_class": "measurement",
        "min_valid": 0,
        "max_valid": 100,
    },
]

# Digital inputs: status (coil 0) + faults (digital inputs).
BINARY_SENSORS = [
    {
        "translation_key": "status",
        "unique_id": "status",
        "address": 0,
        "input_type": "coil",
        "icon": "mdi:check-circle",
    },
    {
        "translation_key": "defaut_general",
        "unique_id": "defaut_general",
        "address": 16,
        "input_type": "discrete_input",
        "icon": "mdi:alert-circle",
        "device_class": "problem",
    },
    {
        "translation_key": "defaut_e3",
        "unique_id": "defaut_e3",
        "address": 51,
        "input_type": "discrete_input",
        "icon": "mdi:alert-circle-outline",
        "device_class": "problem",
    },
]

# Heat pump on/off (coil 0).
SWITCH = {
    "translation_key": "marche_arret",
    "unique_id": "marche_arret",
    "address": 0,
    "input_type": "coil",
    "on_value": 1,
    "off_value": 0,
}

# Temperature setpoint (holding register 3). Same register as the thermostat
# setpoint: both entities re-read the value on the same poll cycle.
NUMBER = {
    "translation_key": "consigne_temperature",
    "unique_id": "consigne_temperature",
    "address": 3,
    "input_type": "holding",
    "scale": 0.5,
    "offset": -30,
    "precision": 1,
    "min": 18,
    "max": 32,
    "step": 0.5,
    "unit": "°C",
    "icon": "mdi:thermometer",
    "device_class": "temperature",
}

# Selects: options -> raw register value.
SELECTS = [
    {
        "translation_key": "mode",
        "unique_id": "mode",
        "address": 0,
        "input_type": "holding",
        "icon": "mdi:air-conditioner",
        "options": {"auto": 0, "heat": 1, "cool": 2},
    },
    {
        "translation_key": "mode_travail",
        "unique_id": "mode_travail",
        "address": 1,
        "input_type": "holding",
        "icon": "mdi:speedometer",
        "options": {"smart": 0, "silence": 1},
    },
]

# Thermostat: current temperature (input 3), setpoint (holding 3), heating
# mode (holding 0) and fan mode (holding 1).
CLIMATE = {
    "translation_key": "thermostat",
    "unique_id": "thermostat",
    "current_temperature": {
        "address": 3,
        "input_type": "input",
        "scale": 0.5,
        "offset": -30,
        "precision": 1,
    },
    "target_temperature": {
        "address": 3,
        "input_type": "holding",
        "scale": 0.5,
        "offset": -30,
        "precision": 1,
        "min": 18,
        "max": 32,
        "step": 0.5,
    },
    "hvac_mode": {
        "address": 0,
        "input_type": "holding",
        "values": {"auto": 0, "heat": 1, "cool": 2},
    },
    "fan_mode": {
        "address": 1,
        "input_type": "holding",
        "values": {"smart": 0, "silence": 1},
    },
}

# ==========================================================================
# Supported brands and models
# --------------------------------------------------------------------------
# Each model provides its own entity set (registers). Adding a
# model = adding one entry in `models` below (+ its translations).
# ==========================================================================

GEPAC08 = {
    "name": "GEPAC08",
    "manufacturer": MANUFACTURER,
    "model": MODEL,
    "sensors": SENSORS,
    "binary_sensors": BINARY_SENSORS,
    "switch": SWITCH,
    "number": NUMBER,
    "selects": SELECTS,
    "climate": CLIMATE,
}

BRANDS = {
    "geco": {
        "name": "Geco",
        "models": {
            "gepac08": GEPAC08,
        },
    },
}

DEFAULT_BRAND = "geco"
DEFAULT_MODEL = "gepac08"


def resolve_model(brand: str, model: str) -> dict:
    """Return the requested model config, falling back to the default."""
    brand_data = BRANDS.get(brand) or BRANDS[DEFAULT_BRAND]
    models = brand_data["models"]
    return models.get(model) or models[DEFAULT_MODEL]
