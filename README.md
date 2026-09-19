# Pool-Heat-Pump-IPHCR45-Modbus

**🌍 Language : [🇫🇷 Français](#français) · [🇬🇧 English](#english) · [🇩🇪 Deutsch](#deutsch) · [🇳🇱 Nederlands](#nederlands)**

![Téléchargements](https://img.shields.io/github/downloads/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus/total?style=for-the-badge&label=T%C3%A9l%C3%A9chargements)
![Dernière version](https://img.shields.io/github/v/release/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus?style=for-the-badge&label=version)

![IPHCR45](custom_components/pool_heat_pump_iphcr45_modbus/brand/logo.png)

---

## Français

Intégration Home Assistant pour piloter une **PAC (pompe à chaleur) de piscine** en **Modbus TCP**, via une passerelle RS485 → Ethernet. **Aucun cloud, aucune connexion Internet** : tout reste local.

La référence **IPHCR45** correspond à une pompe à chaleur de piscine **Full Inverter** haute performance de la marque **Fairland**, souvent distribuée sous différentes marques ou gammes : **Geco / AES / Madimack / BWT / Rapid / Confort**.

Objectif initial : **piloter la pompe à chaleur sans être obligé de passer par le cloud Tuya**.

### Fonctionnalités

| Fonction | Détail | Registre |
|---|---|---|
| Marche / Arrêt | Allume ou éteint la PAC | coil 0 |
| Thermostat | Consigne, mode (Auto/Chaud/Froid), ventilation (Smart/Silence) | holding 3 / holding 0 / holding 1 |
| Température courante | Entrée d'eau | input 3 |
| Température eau (sortie) | Sortie d'eau | input 4 |
| Température air | Ambiante | input 5 |
| Compresseur | Pourcentage de charge | input 0 |
| Intensité compresseur | Courant absorbé | input 11 |
| Tension PFC | Tension interne | input 2 |
| Mode de travail | Smart / Silence | holding 1 |
| Défauts | Défaut général, défaut E3 | discrete 16 / 51 |
| Diagnostic | État de la communication Modbus | — |

Chaque fonction est exposée comme entité dans Home Assistant (voir le tableau des entités plus bas).

### Matériel nécessaire

- Une **passerelle RS485 → Ethernet** (testé : Waveshare RS485 TO ETH / POE).
- Le connecteur **RS485** de la carte de contrôle de la PAC (port prévu pour le module Wi-Fi optionnel).
- Un câble entre la PAC et la passerelle. Un **câble RJ45** convient.

Le port RS485 est le connecteur de la carte de contrôle (broches `B`, `A`, `G`, `+12V`).

### Montage pas à pas

**1. Ouvrir le coffret électrique**

Couper l'alimentation puis **attendre 5 minutes** avant d'ouvrir (voir l'étiquette « CAUTION » sur le capot).

Déposer les vis du dessus et de l'alimentation, puis enlever les caches. Dévisser ensuite les vis du couvercle « CAUTION » et du capot voisin (**7 à 8 vis**).

![Ouverture du coffret](images/open_the_box.jpg)

**2. Repérer le connecteur RS485**

C'est le petit connecteur **4 broches `B`, `A`, `G`, `+12V`** de la carte. C'est le port normalement prévu pour le module Wi-Fi optionnel.

![Repérage du connecteur](images/localise_the_connecteur.jpg)

**3. Câbler le connecteur**

Relier **`B` → `B`**, **`A` → `A`** et **`G` → `GND`**. La passerelle est alimentée en **PoE** : le **`+12V` n'est pas nécessaire**. Un **câble RJ45** convient.

![Câblage du connecteur](images/wire_the_connector.jpg)

### 🛒 Où acheter

| Article | Lien |
|---|---|
| **Kit de connecteurs JST-XH** (2/3/4/5/6 broches, pas 2,54 mm) — pour réaliser le connecteur | [Amazon.fr — YIXISI, 460 pièces](https://www.amazon.fr/dp/B082ZLYRRN) |
| **Passerelle RS485 → Ethernet, 1 canal** | [Amazon.fr — Waveshare](https://www.amazon.fr/dp/B0BRNBTFVC) |
| **Passerelle RS485 → Ethernet, 2 canaux** (une seule passerelle pour deux équipements) | [Amazon.fr — Waveshare](https://www.amazon.fr/dp/B0CB8LXQFH) |

> La version **1 canal** suffit pour la PAC. La version **2 canaux** permet de raccorder deux équipements RS485 avec une seule passerelle (ex. PAC + électrolyseur). Voir aussi la [doc Waveshare](https://www.waveshare.com/wiki/RS485_TO_ETH_(B)).

### Configuration de la passerelle

Dans l'interface web de la passerelle (Waveshare RS485 TO ETH / POE) :

| Réglage | Valeur |
|---|---|
| **Work Mode** | `TCP Server` |
| **Protocol** | `Modbus TCP to RTU` |
| **Device Port** | `4196` (défaut Waveshare ; ici `4197`) |
| **Baud Rate / Databits / Parity / Stopbits** | `9600` / `8` / `None` / `1` |
| **IP mode** | `Static` |
| **Device IP** | IP de la passerelle elle-même |
| **Esclave Modbus** | `1` |

> - **Device IP** : l'adresse IP de la passerelle elle-même ; à adapter à la plage d'adresses (**IP Range**) de ton réseau.
> - **Destination IP** : on peut y mettre la même adresse que **Device IP**, ou l'adresse de **Home Assistant**. Dans notre cas, ce réglage semble sans effet.
> - **Enable Multi-Host** : à activer **en premier** ; c'est ce réglage qui fait apparaître l'option **Time Out**.

![Configuration de la passerelle Waveshare](images/config_waveshare.png)

### Installation de l'intégration

**Via HACS (dépôt personnalisé)**

1. HACS → Intégrations → ⋯ → *Dépôts personnalisés*
2. Ajouter `Locodice67/Pool-Heat-Pump-IPHCR45-Modbus`, catégorie *Intégration*
3. Installer, puis redémarrer Home Assistant

**Manuelle**

Copier le dossier `custom_components/pool_heat_pump_iphcr45_modbus/` dans `/config/custom_components/`, puis redémarrer Home Assistant.

### Configuration

Paramètres → Appareils et services → **Ajouter une intégration** → *Pool-Heat-Pump-IPHCR45-Modbus*.

| Champ | Valeur usuelle |
|---|---|
| Adresse IP | IP de la passerelle RS485 → Ethernet |
| Port TCP | `4196` (valeur par défaut ; modifiable) |
| Adresse Modbus (esclave) | `1` |
| Intervalle de rafraîchissement | `30` s |

L'intervalle est modifiable ensuite via le bouton *Configurer* de l'intégration.

### Entités créées

| Plateforme | Entité | Registre |
|---|---|---|
| `climate` | Thermostat | input 3 / holding 3 / holding 0 / holding 1 |
| `switch` | Marche/Arrêt | coil 0 |
| `number` | Consigne température | holding 3 |
| `select` | Mode (Auto/Chaud/Froid) | holding 0 |
| `select` | Mode de travail | holding 1 |
| `sensor` | Température eau | input 4 |
| `sensor` | Température air | input 5 |
| `sensor` | Intensité compresseur | input 11 |
| `sensor` | Tension PFC | input 2 |
| `sensor` | Compresseur | input 0 |
| `binary_sensor` | Status | coil 0 |
| `binary_sensor` | Défaut général | discrete input 16 |
| `binary_sensor` | Défaut E3 | discrete input 51 |
| `binary_sensor` | État communication Modbus | diagnostic |

> `number` et les deux `select` écrivent **les mêmes registres** que le `climate` : ce sont des vues alternatives. Le `climate` suffit pour piloter la PAC.

### Dashboard

Un simple thermostat + un bouton marche/arrêt + les capteurs suffisent. Exemple d'organisation :

- **Thermostat** (climate) — consigne et mode
- **Marche/Arrêt** (switch)
- **Mesures** — températures eau/air, compresseur, intensité, tension PFC
- **État** — défauts, communication Modbus

### Limitations

- **Mode de travail (registre 1)** : sur l'unité testée (**GEPAC08**), l'**écriture** du registre 1 est **refusée** par la carte (testé avec `0`, `2` et `3`), alors que l'écriture d'autres registres `holding` fonctionne (la consigne, registre 3, passe). Le mode reste donc **lisible** mais **non pilotable** via Modbus sur ce firmware (réglage au clavier de la PAC). À vérifier selon les modèles.
- Les adresses proviennent de la **fiche Modbus officielle des cartes MWH216 / MWH298**. Les cartes **Geco / AES / Madimack / BWT / Rapid / Confort / Fairland** se ressemblent, mais le modèle exact peut différer : vérifie les valeurs (températures eau/air) contre les mesures réelles.

### Matériel de référence

Valeurs relevées sur la plaque signalétique de l'unité de développement.

**GECO — Swimming Pool Heat Pump — modèle `GEPAC08`** (compresseur **INVERTER**)

| Donnée | Valeur | Conditions |
|---|---|---|
| Puissance chauffage | 8,4 kW | air 26 °C / eau 26 °C / 80 % HR |
| COP | 14,1 ~ 7,0 | idem |
| COP à 50 % | 10,3 | idem |
| Puissance chauffage | 6,1 kW | air 15 °C / eau 26 °C / 70 % HR |
| COP | 7,0 ~ 4,8 | idem |
| COP à 50 % | 6,3 | idem |
| Puissance froid | 4,0 kW | air 35 °C / eau 28 °C / 80 % HR |
| Alimentation | 230 V / 1 Ph / 50 Hz | — |
| Pression sonore à 1 m | 38,8 ~ 48,2 dB(A) | — |
| Pression sonore à 50 % | 41,4 dB(A) | — |
| Puissance absorbée | 0,17 ~ 1,2 kW | air 15 °C |
| Courant absorbé | 0,74 ~ 5,2 A | air 15 °C |
| Courant max | 8,5 A | — |
| Débit d'eau conseillé | 2 ~ 4 m³/h | — |
| Fluide frigorigène | R32 — 650 g | GWP 675 · éq. CO₂ 0,439 t |
| Indice de protection | IPX4 | — |
| Poids | 45 kg | — |

### Liens utiles

- [Documentation Modbus de Home Assistant](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))

---

## English

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

### Useful links

- [Home Assistant Modbus documentation](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))

---

## Deutsch

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

### Nützliche Links

- [Home Assistant Modbus-Dokumentation](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))

---

## Nederlands

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

### Nuttige links

- [Home Assistant Modbus-documentatie](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))

---

[⬆️ Haut / Top](#pool-heat-pump-iphcr45-modbus)
