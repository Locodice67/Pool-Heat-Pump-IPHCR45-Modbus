# Pool-Heat-Pump-IPHCR45-Modbus

**🌍 Language : [🇫🇷 Français](README.fr.md) · [🇬🇧 English](README.md) · [🇩🇪 Deutsch](README.de.md) · [🇳🇱 Nederlands](README.nl.md)**

![Téléchargements](https://img.shields.io/github/downloads/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus/total?style=for-the-badge&label=T%C3%A9l%C3%A9chargements)
![Dernière version](https://img.shields.io/github/v/release/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus?style=for-the-badge&label=version)

![IPHCR45](custom_components/pool_heat_pump_iphcr45_modbus/brand/logo.png)

---

Home Assistant integration to control a **swimming pool heat pump** over **Modbus TCP**, through an RS485 → Ethernet gateway. **No cloud, no Internet connection required**: everything runs locally.

The **IPHCR45** reference is a high-performance **Full Inverter** swimming pool heat pump from **Fairland**, often distributed under different brands or ranges: **Geco / AES / Madimack / BWT / Rapid / Confort**.

Original goal: **control the heat pump without going through the Tuya cloud**.

### Features

| Feature | Description | Register |
|---|---|---|
| Power on/off | Turn the heat pump on or off | coil 0 |
| Thermostat | Setpoint, mode (Auto/Heat/Cool), fan (Smart/Silence) | holding 3 / holding 0 / holding 1 |
| Current temperature | Water inlet | input 3 |
| Water outlet temperature | Water outlet | input 4 |
| Ambient temperature | Air | input 5 |
| Compressor | Load percentage | input 0 |
| Compressor current | Current draw | input 11 |
| PFC voltage | Internal voltage | input 2 |
| Working mode | Smart / Silence | holding 1 |
| Faults | General fault, E3 fault | discrete 16 / 51 |
| Diagnostic | Modbus communication status | — |

Every feature is exposed as an entity in Home Assistant (see the entity table below).

### Hardware

- An **RS485 → Ethernet gateway** (tested: Waveshare RS485 TO ETH / POE).
- The **RS485** connector on the heat pump control board (the port intended for the optional Wi-Fi module).
- A cable between the heat pump and the gateway. A **RJ45 cable** is suitable.

The RS485 port is the connector on the control board (pins `B`, `A`, `G`, `+12V`).

### Step-by-step assembly

**1. Open the electrical box**

Switch off the power, then **wait 5 minutes** before opening (see the “CAUTION” label on the cover).

Remove the screws on the top and on the power supply, then take off the covers. Then unscrew the screws of the “CAUTION” cover and of the adjacent hood (**7 to 8 screws**).

![Opening the box](images/open_the_box.jpg)

**2. Locate the RS485 connector**

It is the small **4-pin `B`, `A`, `G`, `+12V`** connector on the board. This is the port normally intended for the optional Wi-Fi module.

![Locating the connector](images/localise_the_connecteur.jpg)

**3. Wire the connector**

Connect **`B` → `B`**, **`A` → `A`** and **`G` → `GND`**. The gateway is powered over **PoE**, so **`+12V` is not needed**. A **RJ45 cable** is suitable.

![Wiring the connector](images/wire_the_connector.jpg)

### 🛒 Where to buy

| Item | Link |
|---|---|
| **JST-XH connector kit** (2/3/4/5/6 pins, 2.54 mm) — to build the connector | [Amazon.co.uk — YIXISI, 460 pcs](https://www.amazon.co.uk/dp/B082ZLYRRN?_encoding=UTF8&ref_=as_li_ss_tl&th=1) |
| **RS485 → Ethernet gateway, 1 channel** | [Amazon.co.uk — Waveshare](https://www.amazon.co.uk/dp/B0BRNBTFVC?_encoding=UTF8&ref_=as_li_ss_tl&psc=1) |
| **RS485 → Ethernet gateway, 2 channels** (a single gateway for two devices) | [Amazon.co.uk — Waveshare](https://www.amazon.co.uk/dp/B0CB8LXQFH?_encoding=UTF8&ref_=as_li_ss_tl&psc=1) |

> The **1-channel** version is enough for the heat pump. The **2-channel** version lets you connect two RS485 devices with a single gateway (e.g. heat pump + electrolyser). See also the [Waveshare docs](https://www.waveshare.com/wiki/RS485_TO_ETH_(B)).

### Gateway configuration

In the gateway web UI (Waveshare RS485 TO ETH / POE):

| Setting | Value |
|---|---|
| **Work Mode** | `TCP Server` |
| **Protocol** | `Modbus TCP to RTU` |
| **Device Port** | `4196` (Waveshare default; here `4197`) |
| **Baud Rate / Databits / Parity / Stopbits** | `9600` / `8` / `None` / `1` |
| **IP mode** | `Static` |
| **Device IP** | The gateway's own IP address |
| **Modbus slave** | `1` |

> - **Device IP**: the gateway's own IP address; keep it consistent with your network's IP range.
> - **Destination IP**: can be set to the same address as **Device IP**, or to **Home Assistant**'s address. In our case this setting appears to have no effect.
> - **Enable Multi-Host**: enable this **first**; it then exposes the **Time Out** setting.

![Waveshare gateway configuration](images/config_waveshare.png)

### Integration installation

**Via HACS (custom repository)**

1. HACS → Integrations → ⋯ → *Custom repositories*
2. Add `Locodice67/Pool-Heat-Pump-IPHCR45-Modbus`, category *Integration*
3. Install, then restart Home Assistant

**Manual**

Copy the `custom_components/pool_heat_pump_iphcr45_modbus/` folder into `/config/custom_components/`, then restart Home Assistant.

### Configuration

Settings → Devices & services → **Add integration** → *Pool-Heat-Pump-IPHCR45-Modbus*.

| Field | Usual value |
|---|---|
| IP address | RS485 → Ethernet gateway IP |
| TCP port | `4196` (default; configurable) |
| Modbus unit (slave) id | `1` |
| Refresh interval | `30` s |

The interval can be changed afterwards through the integration's *Configure* button.

### Created entities

| Platform | Entity | Register |
|---|---|---|
| `climate` | Thermostat | input 3 / holding 3 / holding 0 / holding 1 |
| `switch` | On/Off | coil 0 |
| `number` | Temperature setpoint | holding 3 |
| `select` | Mode (Auto/Heat/Cool) | holding 0 |
| `select` | Working mode | holding 1 |
| `sensor` | Water temperature | input 4 |
| `sensor` | Air temperature | input 5 |
| `sensor` | Compressor current | input 11 |
| `sensor` | PFC voltage | input 2 |
| `sensor` | Compressor | input 0 |
| `binary_sensor` | Status | coil 0 |
| `binary_sensor` | General fault | discrete input 16 |
| `binary_sensor` | E3 fault | discrete input 51 |
| `binary_sensor` | Modbus communication status | diagnostic |

> `number` and both `select` entities write **the same registers** as the `climate`: they are alternative views. The `climate` alone is enough to control the heat pump.

### Dashboard

A thermostat plus an on/off button and the sensors are enough. Suggested layout:

- **Thermostat** (climate) — setpoint and mode
- **On/Off** (switch)
- **Measurements** — water/air temperatures, compressor, current, PFC voltage
- **Status** — faults, Modbus communication

### Limitations

- **Working mode (register 1)**: on the tested unit (**GEPAC08**) the **write** to register 1 is **rejected** by the board (tested with `0`, `2` and `3`), while other `holding` writes work (the setpoint, register 3, goes through). The mode is therefore **readable** but **not controllable** over Modbus on this firmware (it is set on the heat pump keypad). Model dependent.
- The addresses come from the **official Modbus documentation for the MWH216 / MWH298 boards**. **Geco / AES / Madimack / BWT / Rapid / Confort / Fairland** boards look alike, but the exact model may differ: verify the values (water/air temperatures) against actual measurements.

### Reference hardware

Values read from the nameplate of the development unit.

**GECO — Swimming Pool Heat Pump — model `GEPAC08`** (**INVERTER** compressor)

| Data | Value | Conditions |
|---|---|---|
| Heating capacity | 8.4 kW | air 26 °C / water 26 °C / 80 % RH |
| COP | 14.1 ~ 7.0 | idem |
| COP at 50 % | 10.3 | idem |
| Heating capacity | 6.1 kW | air 15 °C / water 26 °C / 70 % RH |
| COP | 7.0 ~ 4.8 | idem |
| COP at 50 % | 6.3 | idem |
| Cooling capacity | 4.0 kW | air 35 °C / water 28 °C / 80 % RH |
| Power supply | 230 V / 1 Ph / 50 Hz | — |
| Sound pressure at 1 m | 38.8 ~ 48.2 dB(A) | — |
| Sound pressure at 50 % | 41.4 dB(A) | — |
| Rated input power | 0.17 ~ 1.2 kW | air 15 °C |
| Rated input current | 0.74 ~ 5.2 A | air 15 °C |
| Max input current | 8.5 A | — |
| Advised water flux | 2 ~ 4 m³/h | — |
| Refrigerant | R32 — 650 g | GWP 675 · CO₂e 0.439 t |
| Protection level | IPX4 | — |
| Weight | 45 kg | — |

### Credits

This integration is based on the registers, wiring notes and groundwork from [spdr870/fairland_iphcr45_modbus](https://github.com/spdr870/fairland_iphcr45_modbus) by [@spdr870](https://github.com/spdr870). Many thanks for sharing the original reverse-engineering work — it made this Home Assistant integration possible.

### Useful links

- [Home Assistant Modbus documentation](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))
