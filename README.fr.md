# Pool-Heat-Pump-IPHCR45-Modbus

**🌍 Language : [🇫🇷 Français](README.fr.md) · [🇬🇧 English](README.md) · [🇩🇪 Deutsch](README.de.md) · [🇳🇱 Nederlands](README.nl.md)**

![Téléchargements](https://img.shields.io/github/downloads/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus/total?style=for-the-badge&label=T%C3%A9l%C3%A9chargements)
![Dernière version](https://img.shields.io/github/v/release/Locodice67/Pool-Heat-Pump-IPHCR45-Modbus?style=for-the-badge&label=version)

![IPHCR45](custom_components/pool_heat_pump_iphcr45_modbus/brand/logo.png)

---

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

### Remerciements

Cette intégration s'appuie sur les registres, les notes de câblage et le travail initial de [spdr870/fairland_iphcr45_modbus](https://github.com/spdr870/fairland_iphcr45_modbus) par [@spdr870](https://github.com/spdr870). Merci d'avoir partagé ce travail de rétro-ingénierie — il a rendu cette intégration Home Assistant possible.

### Liens utiles

- [Documentation Modbus de Home Assistant](https://www.home-assistant.io/integrations/modbus/)
- [Waveshare RS485 TO ETH (B)](https://www.waveshare.com/wiki/RS485_TO_ETH_(B))
