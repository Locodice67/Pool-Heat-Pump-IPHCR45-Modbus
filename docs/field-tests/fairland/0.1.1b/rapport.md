# Test de l'intégration Fairland 0.1.1 — 2e série, essais A à D

**Matériel** : PAC Fairland GEPAC08, carte **MWH298-V3**, passerelle **Waveshare 2-CH RS485 to POE ETH (B)**, port 4196, adresse Modbus 1.
**Home Assistant** 2026.10.2, langue `fr`. Intégration `fairland` 0.1.1 (aucune mise à jour faite), entrée `01M5KQG9HWJCDJ1GY04WKRRFD2`.
**Conditions** : eau 14,5 °C, air ~14,5 °C, filtration en marche. Toutes les écritures sont passées par les services Home Assistant, aucune écriture Modbus directe.

## Essai A — contrôleur de débit

| Relevé | Heure | Discrete à 1 | Coils à 1 | input 0 | input 10 | input 11 | Codes actifs |
|---|---|---|---|---|---|---|---|
| A1 filtration en marche | 20:34:56 | 0, 2, 3, 4, 5, 6, 8, 17 | 0, 16, 32 | 54 | 48 | 7 | aucun |
| A2 coupure + 10 s | 20:35:50 | 0, 2, 3, 5, 6, 8, 16, 51 | 0, 16, 32 | 0 | 0 | 0 | **E3** |
| A3 coupure + 90 s | 20:37:11 | 0, 2, 3, 5, 6, 16, 51 | 0, 16, 32 | 0 | 0 | 0 | **E3** |
| A4 retour + 10 s | 20:38:06 | 0, 2, 3, 4, 5, 6, 8 | 0, 16, 32 | 0 | 0 | 0 | aucun |
| A4b retour + 30 s | 20:38:28 | 0, 2, 3, 4, 5, 6, 8 | 0, 16, 32 | 0 | 0 | 0 | aucun |

Confirmation de Manu : coupure à **20:35:39**, retour à **20:37:55**.

Bits qui changent :

| Bit | A1 | A2 | A3 | A4 |
|---|---|---|---|---|
| **4** | 1 | **0** | **0** | **1** |
| **8 (OUT2)** | 1 | 1 | **0** | **1** |
| **17** | 1 | **0** | 0 | 0 |
| **16** | 0 | **1** | 1 | **0** |
| **51** | 0 | **1** | 1 | **0** |

- **discrete 4** tombe dès A2, donc dans les 10 s suivant la coupure et avant l'arrêt complet : cohérent avec un contrôleur de débit.
- **discrete 8 (OUT2)** ne tombe pas à 10 s mais à 90 s, et remonte en moins de 10 s au retour du débit **alors que le compresseur était encore à 0 %**. Il suit la présence de débit avec du retard, ni le compresseur ni le mode.
- **discrete 17** est à 1 seulement quand la machine tourne (A1, B1, B2) et tombe à l'arrêt.
- **discrete 16 et 51** apparaissent uniquement à l'arrêt sur défaut (A2, A3) et disparaissent au retour du débit.
- Le code **E3** était déjà actif à **10 s** lors de cette coupure. Lors de la campagne précédente il était apparu à 45 s : la différence est que le compresseur tournait ici à 58 % et là à 100 %.

## Essai B — OUT2 en chauffage et en froid

| Relevé | Heure | Mode | Consigne | Discrete à 1 | input 0 | input 10 | input 11 | holding 0 | Codes |
|---|---|---|---|---|---|---|---|---|---|
| B1 chauffage | 20:39:44 | heat | 28 °C | 0, 2, 3, 4, 5, 6, 8, 17 | 46 | 40 | 5 | **1** | aucun |
| B2 froid | 20:43:57 | cool | 12 °C | 0, 2, 3, 4, 5, 6, 8, **12**, 17 | 76 | 50 | 8 | **2** | aucun |

- **discrete 8 ne change pas** entre le chauffage et le froid : ce n'est donc pas la vanne 4 voies.
- **discrete 12 apparaît uniquement en froid** et disparaît au retour en chauffage : c'est la seule sortie entre 7 et 15 qui bascule avec l'inversion de cycle.
- `holding` 0 vaut **1 en chauffage et 2 en froid**. Cela ne correspond pas au mapping annoncé (registre 2 en auto, 3 en chauffage, 4 en refroidissement) : ici c'est le registre 0 qui porte le mode, avec 1 = chaud et 2 = froid.
- Consigne de froid d'origine avant modification : **20 °C**. Le minimum accepté par l'entité en froid est bien **12 °C** (en chaud : 18 à 40).
- Compresseur redémarré **3 min 30** après le passage en froid (sensor à 58 %, `input.0` à 76 % au relevé B2).
- Après l'essai, consigne de chauffe d'origine **28 °C** rétablie et retour en `heat` accepté.

## Essai C — courant

Puissance et courant relevés sur le compteur de la prise de la PAC (`sensor.prise_pac_piscine_*`), alignés à la seconde avec `input.10` et `input.11`.

| Compresseur | input 10 (Hz) | input 11 | Intégration (0,1 A/unité) | Mesuré sur la prise | Facteur réel |
|---|---|---|---|---|---|
| arrêté | 0 | 1 | 0,1 A | 97–138 W / 0,73–0,85 A | — |
| montée | 26 | 2 | 0,2 A | 167 W / 0,94 A | 0,47 |
| montée | 32 | 3 | 0,3 A | 214 W / 1,11 A | 0,37 |
| montée | 38 | 5 | 0,5 A | 259 W / 1,28 A | 0,26 |
| montée | 44 | 6 | 0,6 A | 364 W / 1,69 A | 0,28 |
| **régime** | **50** | **8** | **0,8 A** | **433–444 W / 1,97–2,03 A** | **0,25** |
| régime | 72 | 14 | 1,4 A | 653 W / 2,90 A | 0,21 |
| **pleine charge** | **84** | **20** | **2,0 A** | **895 W / 3,90 A** | **0,195** |

L'écart entre la valeur de l'intégration et la mesure réelle est d'un facteur **2 à 2,5**, et il n'est pas constant : il diminue quand la vitesse augmente. L'hypothèse d'un facteur 10 ne se vérifie pas sur ces relevés.

## Essai D — vérifications rapides

**D1. Préréglage `turbo` depuis l'interface web** (pas par l'API) : le message s'affiche bien **en français**, mot pour mot :

> La pompe à chaleur n'est pas passée sur ce préréglage. Certains modèles n'ont pas tous les modes de fonctionnement, et certains n'acceptent Smart que lorsque le compresseur tourne.

Le préréglage est resté sur **`silence`** après l'essai. Par l'API REST le même refus renvoie le message **en anglais**, alors que l'interface affiche la version française : la traduction fonctionne côté interface, pas côté réponse API.

**D2. Réponses de Manu**

- Passerelle Modbus TCP : **Waveshare 2-CH RS485 to POE ETH (B)**
- Carte électronique : **MWH298-V3** (sérigraphie photographiée, visible sous le faisceau de câblage)

## État final de la PAC

Mode `heat`, consigne **28 °C**, préréglage `silence`, compresseur arrêté par la remise en `off`, filtration laissée en marche comme à l'arrivée. Aucun code défaut actif.

## Fichiers joints

`diag-A1-filtration-on.json`, `diag-A2-off-10s.json`, `diag-A3-off-90s.json`, `diag-A4-on-10s.json`, `diag-A4b-on-30s.json`, `diag-B1-heat.json`, `diag-B2-cool.json`, `diag-D1-apres-turbo-ui.json`, plus `releves.json` (tableau des huit relevés) et `essai-C-courant.json` (tableau des cent vingt échantillons de l'essai C).
