# Pool-Heat-Pump-IPHCR45-Modbus

**🌍 Language : [🇫🇷 Français](README.fr.md) · [🇬🇧 English](README.md) · [🇩🇪 Deutsch](README.de.md) · [🇳🇱 Nederlands](README.nl.md)**

![Téléchargements](https://img.shields.io/github/downloads/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus/total?style=for-the-badge&label=T%C3%A9l%C3%A9chargements)
![Dernière version](https://img.shields.io/github/v/release/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus?style=for-the-badge&label=version)

![IPHCR45](custom_components/pool_heat_pump_iphcr45_modbus/brand/logo.png)

---

Home Assistant Integration zur Steuerung einer **Pool-Wärmepumpe** über **Modbus TCP**, mittels eines RS485-→-Ethernet-Gateways. **Keine Cloud, keine Internetverbindung**: alles läuft lokal.

Die Referenz **IPHCR45** entspricht einer Hochleistungs-**Full-Inverter**-Pool-Wärmepumpe der Marke **Fairland**, die häufig unter verschiedenen Marken oder Baureihen vertrieben wird: **Geco / AES / Madimack / BWT / Rapid / Confort**.

Ursprüngliches Ziel: **die Wärmepumpe steuern, ohne die Tuya-Cloud nutzen zu müssen**.

### Funktionen

| Funktion | Details | Register |
|---|---|---|
| Ein / Aus | Schaltet die Wärmepumpe ein oder aus | coil 0 |
| Thermostat | Sollwert, Modus (Auto/Heizen/Kühlen), Lüftung (Smart/Silence) | holding 3 / holding 0 / holding 1 |
| Aktuelle Temperatur | Wassereintritt | input 3 |
| Wassertemperatur (Austritt) | Wasseraustritt | input 4 |
| Lufttemperatur | Umgebung | input 5 |
| Kompressor | Last in Prozent | input 0 |
| Kompressorstrom | Aufgenommener Strom | input 11 |
| PFC-Spannung | Interne Spannung | input 2 |
| Betriebsmodus | Smart / Silence | holding 1 |
| Störungen | Allgemeiner Fehler, Fehler E3 | discrete 16 / 51 |
| Diagnose | Status der Modbus-Kommunikation | — |

Jede Funktion wird als Entität in Home Assistant bereitgestellt (siehe Entitätstabelle weiter unten).

### Erforderliche Hardware

- Ein **RS485-→-Ethernet-Gateway** (getestet: Waveshare RS485 TO ETH / POE).
- Der **RS485**-Anschluss der Steuerplatine der Wärmepumpe (für das optionale Wi-Fi-Modul vorgesehen).
- Ein Kabel zwischen Wärmepumpe und Gateway. Ein **RJ45-Kabel** ist geeignet.

Der RS485-Anschluss ist der Steckverbinder auf der Steuerplatine (Pins `B`, `A`, `G`, `+12V`).

### Montage Schritt für Schritt

**1. Elektrisches Gehäuse öffnen**

Die Stromversorgung abschalten und **5 Minuten warten**, bevor Sie öffnen (siehe „CAUTION“-Aufkleber auf der Abdeckung).

Die Schrauben oben und an der Stromversorgung entfernen, dann die Abdeckungen abnehmen. Anschließend die Schrauben der „CAUTION“-Abdeckung und der benachbarten Haube lösen (**7 bis 8 Schrauben**).

![Öffnen des Gehäuses](images/open_the_box.jpg)

**2. RS485-Anschluss finden**

Es ist der kleine **4-polige Steckverbinder `B`, `A`, `G`, `+12V`** auf der Platine. Dies ist der normalerweise für das optionale Wi-Fi-Modul vorgesehene Anschluss.

![Finden des Anschlusses](images/localise_the_connecteur.jpg)

**3. Anschluss verdrahten**

**`B` → `B`**, **`A` → `A`** und **`G` → `GND`** verbinden. Das Gateway wird über **PoE** versorgt: **`+12V` wird nicht benötigt**. Ein **RJ45-Kabel** ist geeignet.

![Verdrahtung des Anschlusses](images/wire_the_connector.jpg)

### 🛒 Wo kaufen

| Artikel | Link |
|---|---|
| **JST-XH-Steckverbinder-Set** (2/3/4/5/6 Pins, Raster 2,54 mm) — für den Steckverbinder | [Amazon.de — YIXISI, 460 Stück](https://www.amazon.de/dp/B082ZLYRRN?_encoding=UTF8&ref_=as_li_ss_tl&th=1) |
| **RS485-→-Ethernet-Gateway, 1 Kanal** | [Amazon.de — Waveshare](https://www.amazon.de/dp/B0BRNBTFVC?_encoding=UTF8&ref_=as_li_ss_tl&psc=1) |
| **RS485-→-Ethernet-Gateway, 2 Kanäle** (ein Gateway für zwei Geräte) | [Amazon.de — Waveshare](https://www.amazon.de/dp/B0CB8LXQFH?_encoding=UTF8&ref_=as_li_ss_tl&psc=1) |

> Die **1-Kanal**-Version genügt für die Wärmepumpe. Die **2-Kanal**-Version erlaubt zwei RS485-Geräte an einem Gateway (z. B. Wärmepumpe + Elektrolysegerät). Siehe auch die [Waveshare-Doku](https://www.waveshare.com/wiki/RS485_TO_ETH_(B)).

### Gateway-Konfiguration

In der Weboberfläche des Gateways (Waveshare RS485 TO ETH / POE):

| Einstellung | Wert |
|---|---|
| **Work Mode** | `TCP Server` |
| **Protocol** | `Modbus TCP to RTU` |
| **Device Port** | `4196` (Waveshare-Standard; hier `4197`) |
| **Baud Rate / Databits / Parity / Stopbits** | `9600` / `8` / `None` / `1` |
| **IP mode** | `Static` |
| **Device IP** | IP des Gateways selbst |
| **Modbus-Slave** | `1` |

> - **Device IP**: die IP-Adresse des Gateways selbst; an den Adressbereich (**IP Range**) Ihres Netzwerks anzupassen.
> - **Destination IP**: kann dieselbe Adresse wie **Device IP** oder die Adresse von **Home Assistant** sein. In unserem Fall scheint diese Einstellung wirkungslos.
> - **Enable Multi-Host**: **zuerst** aktivieren; diese Einstellung blendet die Option **Time Out** ein.

![Gateway-Konfiguration Waveshare](images/config_waveshare.png)

### Installation der Integration

**Über HACS (benutzerdefiniertes Repository)**

1. HACS → Integrationen → ⋯ → *Benutzerdefinierte Repositories*
2. `Locodice67/Pool-Heat-Pump-IPHCR45-Modbus` hinzufügen, Kategorie *Integration*
3. Installieren, dann Home Assistant neu starten

**Manuell**

Den Ordner `custom_components/pool_heat_pump_iphcr45_modbus/` nach `/config/custom_components/` kopieren, dann Home Assistant neu starten.

### Konfiguration

Einstellungen → Geräte & Dienste → **Integration hinzufügen** → *Pool-Heat-Pump-IPHCR45-Modbus*.

| Feld | Üblicher Wert |
|---|---|
| IP-Adresse | IP des RS485-→-Ethernet-Gateways |
| TCP-Port | `4196` (Standardwert; änderbar) |
| Modbus-Adresse (Slave) | `1` |
| Aktualisierungsintervall | `30` s |

Das Intervall ist anschließend über die Schaltfläche *Konfigurieren* der Integration änderbar.

### Erstellte Entitäten

| Plattform | Entität | Register |
|---|---|---|
| `climate` | Thermostat | input 3 / holding 3 / holding 0 / holding 1 |
| `switch` | Ein/Aus | coil 0 |
| `number` | Solltemperatur | holding 3 |
| `select` | Modus (Auto/Heizen/Kühlen) | holding 0 |
| `select` | Betriebsmodus | holding 1 |
| `sensor` | Wassertemperatur | input 4 |
| `sensor` | Lufttemperatur | input 5 |
| `sensor` | Kompressorstrom | input 11 |
| `sensor` | PFC-Spannung | input 2 |
| `sensor` | Kompressor | input 0 |
| `binary_sensor` | Status | coil 0 |
| `binary_sensor` | Allgemeiner Fehler | discrete input 16 |
| `binary_sensor` | Fehler E3 | discrete input 51 |
| `binary_sensor` | Modbus-Kommunikationsstatus | diagnostic |

> `number` und beide `select` schreiben **dieselben Register** wie das `climate`: sie sind alternative Ansichten. Das `climate` allein genügt zur Steuerung der Wärmepumpe.

### Dashboard

Ein einfaches Thermostat + eine Ein/Aus-Schaltfläche + die Sensoren genügen. Beispiel einer Organisation:

- **Thermostat** (climate) — Sollwert und Modus
- **Ein/Aus** (switch)
- **Messwerte** — Wasser-/Lufttemperatur, Kompressor, Strom, PFC-Spannung
- **Status** — Störungen, Modbus-Kommunikation

### Einschränkungen

- **Betriebsmodus (Register 1)**: Beim getesteten Gerät (**GEPAC08**) wird das **Schreiben** von Register 1 von der Platine **abgelehnt** (getestet mit `0`, `2` und `3`), während das Schreiben anderer `holding`-Register funktioniert (der Sollwert, Register 3, geht durch). Der Modus ist daher **lesbar**, aber über Modbus in dieser Firmware **nicht steuerbar** (Einstellung über die Tastatur der Wärmepumpe). Je nach Modell zu prüfen.
- Die Adressen stammen aus dem **offiziellen Modbus-Datenblatt der Platinen MWH216 / MWH298**. Die Platinen **Geco / AES / Madimack / BWT / Rapid / Confort / Fairland** ähneln sich, das genaue Modell kann jedoch abweichen: Prüfen Sie die Werte (Wasser-/Lufttemperatur) gegen die tatsächlichen Messungen.

### Referenzhardware

Werte vom Typenschild des Entwicklungsgeräts.

**GECO — Swimming Pool Heat Pump — Modell `GEPAC08`** (**INVERTER**-Kompressor)

| Angabe | Wert | Bedingungen |
|---|---|---|
| Heizleistung | 8,4 kW | Luft 26 °C / Wasser 26 °C / 80 % rF |
| COP | 14,1 ~ 7,0 | dito |
| COP bei 50 % | 10,3 | dito |
| Heizleistung | 6,1 kW | Luft 15 °C / Wasser 26 °C / 70 % rF |
| COP | 7,0 ~ 4,8 | dito |
| COP bei 50 % | 6,3 | dito |
| Kühlleistung | 4,0 kW | Luft 35 °C / Wasser 28 °C / 80 % rF |
| Stromversorgung | 230 V / 1 Ph / 50 Hz | — |
| Schalldruck bei 1 m | 38,8 ~ 48,2 dB(A) | — |
| Schalldruck bei 50 % | 41,4 dB(A) | — |
| Aufgenommene Leistung | 0,17 ~ 1,2 kW | Luft 15 °C |
| Aufgenommener Strom | 0,74 ~ 5,2 A | Luft 15 °C |
| Max. Strom | 8,5 A | — |
| Empfohlener Wasserdurchfluss | 2 ~ 4 m³/h | — |
| Kältemittel | R32 — 650 g | GWP 675 · CO₂e 0,439 t |
| Schutzart | IPX4 | — |
| Gewicht | 45 kg | — |

### Danksagung

Diese Integration basiert auf den Registern, Verkabelungshinweisen und der Vorarbeit von [spdr870/fairland_iphcr45_modbus](https://github.com/spdr870/fairland_iphcr45_modbus) von [@spdr870](https://github.com/spdr870). Vielen Dank für das Teilen der ursprünglichen Reverse-Engineering-Arbeit — sie hat diese Home-Assistant-Integration ermöglicht.

### Nützliche Links

- [Home Assistant Modbus-Dokumentation](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))
