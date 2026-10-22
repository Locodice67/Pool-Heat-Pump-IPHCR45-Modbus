# Pool-Heat-Pump-IPHCR45-Modbus

**🌍 Language : [🇫🇷 Français](README.fr.md) · [🇬🇧 English](README.md) · [🇩🇪 Deutsch](README.de.md) · [🇳🇱 Nederlands](README.nl.md)**

![Téléchargements](https://img.shields.io/github/downloads/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus/total?style=for-the-badge&label=T%C3%A9l%C3%A9chargements)
![Dernière version](https://img.shields.io/github/v/release/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus?style=for-the-badge&label=version)

![IPHCR45](custom_components/pool_heat_pump_iphcr45_modbus/brand/logo.png)

---

Home Assistant-integratie om een **zwembadwarmtepomp** aan te sturen via **Modbus TCP**, met een RS485-→-Ethernet-gateway. **Geen cloud, geen internetverbinding**: alles blijft lokaal.

De referentie **IPHCR45** komt overeen met een hoogwaardige **Full Inverter**-zwembadwarmtepomp van het merk **Fairland**, die vaak onder verschillende merken of reeksen wordt verdeeld: **Geco / AES / Madimack / BWT / Rapid / Confort**.

Oorspronkelijk doel: **de warmtepomp aansturen zonder via de Tuya-cloud te moeten gaan**.

### Functies

| Functie | Detail | Register |
|---|---|---|
| Aan / Uit | Schakelt de warmtepomp aan of uit | coil 0 |
| Thermostaat | Setpoint, modus (Auto/Verwarmen/Koelen), ventilatie (Smart/Silence) | holding 3 / holding 0 / holding 1 |
| Huidige temperatuur | Waterinlaat | input 3 |
| Watertemperatuur (uitlaat) | Wateruitlaat | input 4 |
| Luchttemperatuur | Omgeving | input 5 |
| Compressor | Belasting in procent | input 0 |
| Compressorstroom | Opgenomen stroom | input 11 |
| PFC-spanning | Interne spanning | input 2 |
| Werkmodus | Smart / Silence | holding 1 |
| Storingen | Algemene fout, fout E3 | discrete 16 / 51 |
| Diagnose | Status van de Modbus-communicatie | — |

Elke functie wordt als entiteit in Home Assistant weergegeven (zie de entiteitentabel hieronder).

### Benodigde hardware

- Een **RS485-→-Ethernet-gateway** (getest: Waveshare RS485 TO ETH / POE).
- De **RS485**-connector op de regelkaart van de warmtepomp (de poort die bedoeld is voor de optionele Wi-Fi-module).
- Een kabel tussen de warmtepomp en de gateway. Een **RJ45-kabel** volstaat.

De RS485-poort is de connector op de regelkaart (pinnen `B`, `A`, `G`, `+12V`).

### Montage stap voor stap

**1. De elektrische kast openen**

Schakel de voeding uit en **wacht 5 minuten** voordat u opent (zie het label „CAUTION“ op de kap).

Verwijder de schroeven bovenop en bij de voeding en neem de afdekkingen weg. Draai daarna de schroeven van de „CAUTION“-kap en van de aangrenzende kap los (**7 tot 8 schroeven**).

![De kast openen](images/open_the_box.jpg)

**2. De RS485-connector vinden**

Het is de kleine **4-pins connector `B`, `A`, `G`, `+12V`** op de kaart. Dit is de poort die normaal voor de optionele Wi-Fi-module bedoeld is.

![De connector vinden](images/localise_the_connecteur.jpg)

**3. De connector aansluiten**

Verbind **`B` → `B`**, **`A` → `A`** en **`G` → `GND`**. De gateway wordt via **PoE** gevoed: **`+12V` is niet nodig**. Een **RJ45-kabel** volstaat.

![De connector aansluiten](images/wire_the_connector.jpg)

### 🛒 Waar kopen

| Artikel | Link |
|---|---|
| **JST-XH-connectorkit** (2/3/4/5/6 pinnen, pitch 2,54 mm) — om de connector te maken | [Amazon.nl — YIXISI, 460 stuks](https://www.amazon.nl/dp/B082ZLYRRN?_encoding=UTF8&ref_=as_li_ss_tl&th=1) |
| **RS485-→-Ethernet-gateway, 1 kanaal** | [Amazon.nl — Waveshare](https://www.amazon.nl/dp/B0BRNBTFVC?_encoding=UTF8&ref_=as_li_ss_tl&psc=1) |
| **RS485-→-Ethernet-gateway, 2 kanalen** (één gateway voor twee apparaten) | [Amazon.nl — Waveshare](https://www.amazon.nl/dp/B0CB8LXQFH?_encoding=UTF8&ref_=as_li_ss_tl&psc=1) |

> De **1-kanaals** versie volstaat voor de warmtepomp. De **2-kanaals** versie laat twee RS485-apparaten op één gateway toe (bv. warmtepomp + elektrolyseur). Zie ook de [Waveshare-docs](https://www.waveshare.com/wiki/RS485_TO_ETH_(B)).

### Gateway-configuratie

In de webinterface van de gateway (Waveshare RS485 TO ETH / POE):

| Instelling | Waarde |
|---|---|
| **Work Mode** | `TCP Server` |
| **Protocol** | `Modbus TCP to RTU` |
| **Device Port** | `4196` (Waveshare-standaard; hier `4197`) |
| **Baud Rate / Databits / Parity / Stopbits** | `9600` / `8` / `None` / `1` |
| **IP mode** | `Static` |
| **Device IP** | IP van de gateway zelf |
| **Modbus-slave** | `1` |

> - **Device IP**: het IP-adres van de gateway zelf; aan te passen aan het adresbereik (**IP Range**) van uw netwerk.
> - **Destination IP**: u kunt hier hetzelfde adres als **Device IP** gebruiken, of het adres van **Home Assistant**. In ons geval lijkt deze instelling geen effect te hebben.
> - **Enable Multi-Host**: **eerst** activeren; deze instelling maakt de optie **Time Out** zichtbaar.

![Gateway-configuratie Waveshare](images/config_waveshare.png)

### De integratie installeren

**Via HACS (aangepaste repository)**

1. HACS → Integraties → ⋯ → *Aangepaste repositories*
2. `Locodice67/Pool-Heat-Pump-IPHCR45-Modbus` toevoegen, categorie *Integratie*
3. Installeren en Home Assistant opnieuw opstarten

**Handmatig**

Kopieer de map `custom_components/pool_heat_pump_iphcr45_modbus/` naar `/config/custom_components/` en start Home Assistant opnieuw op.

### Configuratie

Instellingen → Apparaten & diensten → **Integratie toevoegen** → *Pool-Heat-Pump-IPHCR45-Modbus*.

| Veld | Gebruikelijke waarde |
|---|---|
| IP-adres | IP van de RS485-→-Ethernet-gateway |
| TCP-poort | `4196` (standaardwaarde; aanpasbaar) |
| Modbus-adres (slave) | `1` |
| Verversingsinterval | `30` s |

Het interval kan achteraf worden gewijzigd via de knop *Configureren* van de integratie.

### Aangemaakte entiteiten

| Platform | Entiteit | Register |
|---|---|---|
| `climate` | Thermostaat | input 3 / holding 3 / holding 0 / holding 1 |
| `switch` | Aan/Uit | coil 0 |
| `number` | Gewenste temperatuur | holding 3 |
| `select` | Modus (Auto/Verwarmen/Koelen) | holding 0 |
| `select` | Werkmodus | holding 1 |
| `sensor` | Watertemperatuur | input 4 |
| `sensor` | Luchttemperatuur | input 5 |
| `sensor` | Compressorstroom | input 11 |
| `sensor` | PFC-spanning | input 2 |
| `sensor` | Compressor | input 0 |
| `binary_sensor` | Status | coil 0 |
| `binary_sensor` | Algemene fout | discrete input 16 |
| `binary_sensor` | Fout E3 | discrete input 51 |
| `binary_sensor` | Modbus-communicatiestatus | diagnostic |

> `number` en beide `select` schrijven **dezelfde registers** als de `climate`: het zijn alternatieve weergaven. De `climate` alleen volstaat om de warmtepomp aan te sturen.

### Dashboard

Een eenvoudige thermostaat + een aan/uit-knop + de sensoren volstaan. Voorbeeld van een indeling:

- **Thermostaat** (climate) — setpoint en modus
- **Aan/Uit** (switch)
- **Metingen** — water-/luchttemperatuur, compressor, stroom, PFC-spanning
- **Status** — storingen, Modbus-communicatie

### Beperkingen

- **Werkmodus (register 1)**: op het geteste toestel (**GEPAC08**) wordt het **schrijven** van register 1 door de kaart **geweigerd** (getest met `0`, `2` en `3`), terwijl het schrijven van andere `holding`-registers werkt (het setpoint, register 3, gaat door). De modus is dus **leesbaar**, maar via Modbus op deze firmware **niet aanstuurbaar** (instelling via het toetsenbord van de warmtepomp). Afhankelijk van het model te controleren.
- De adressen komen uit het **officiële Modbus-datasheet van de kaarten MWH216 / MWH298**. De kaarten **Geco / AES / Madimack / BWT / Rapid / Confort / Fairland** lijken op elkaar, maar het exacte model kan afwijken: controleer de waarden (water-/luchttemperatuur) tegen de werkelijke metingen.

### Referentiehardware

Waarden van het typeplaatje van het ontwikkelingstoestel.

**GECO — Swimming Pool Heat Pump — model `GEPAC08`** (**INVERTER**-compressor)

| Gegeven | Waarde | Omstandigheden |
|---|---|---|
| Verwarmingsvermogen | 8,4 kW | lucht 26 °C / water 26 °C / 80 % RV |
| COP | 14,1 ~ 7,0 | idem |
| COP bij 50 % | 10,3 | idem |
| Verwarmingsvermogen | 6,1 kW | lucht 15 °C / water 26 °C / 70 % RV |
| COP | 7,0 ~ 4,8 | idem |
| COP bij 50 % | 6,3 | idem |
| Koelvermogen | 4,0 kW | lucht 35 °C / water 28 °C / 80 % RV |
| Voeding | 230 V / 1 Ph / 50 Hz | — |
| Geluidsdruk op 1 m | 38,8 ~ 48,2 dB(A) | — |
| Geluidsdruk bij 50 % | 41,4 dB(A) | — |
| Opgenomen vermogen | 0,17 ~ 1,2 kW | lucht 15 °C |
| Opgenomen stroom | 0,74 ~ 5,2 A | lucht 15 °C |
| Max. stroom | 8,5 A | — |
| Aanbevolen waterdebiet | 2 ~ 4 m³/h | — |
| Koelmiddel | R32 — 650 g | GWP 675 · CO₂e 0,439 t |
| Beschermingsgraad | IPX4 | — |
| Gewicht | 45 kg | — |

### Dankbetuiging

Deze integratie is gebaseerd op de registers, bekabelingsnotities en het voorwerk van [spdr870/fairland_iphcr45_modbus](https://github.com/spdr870/fairland_iphcr45_modbus) door [@spdr870](https://github.com/spdr870). Hartelijk dank voor het delen van het oorspronkelijke reverse-engineeringwerk — het maakte deze Home Assistant-integratie mogelijk.

### Nuttige links

- [Home Assistant Modbus-documentatie](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))

---

[⬆️ Haut / Top](#pool-heat-pump-iphcr45-modbus)
