# Essai E — intégration Fairland 0.1.1, PAC GEPAC08

**Date** : 24 octobre 2026, 10 h 31 → 10 h 37 (Europe/Paris)
**Demandeur** : chpego, issue #2 de `Locodice67/Pool-Heat-Pump-IPHCR45-Modbus`
**Question posée** : DIN3 (entrée discrète 4) suit-il le débit d'eau même quand la PAC est arrêtée ? Si oui, un vrai capteur « débit d'eau » est possible.

## Conditions du test

- PAC alimentée à 10 h 31 (le relais Tongou `switch.prise_pac_piscine` était coupé depuis la veille), filtration en marche depuis 7 h 00.
- Aucune écriture Modbus : uniquement `climate.turn_off`, `climate.set_hvac_mode`, `climate.set_temperature` (étape 0 seulement) et `switch.turn_on/turn_off` sur la filtration.
- Aucun préréglage touché (resté `silence`), P1–P5 et dégivrage non touchés.
- Défaut E3 attendu pendant la coupure de filtration.

## Étape 0 — remise en ordre de la consigne de froid

| Registre | Avant | Après |
|---|---|---|
| `holding 3` (consigne chauffage) | 116 → 28,0 °C | 116 → 28,0 °C (inchangé) |
| `holding 4` (consigne froid) | 116 → 28,0 °C (anomalie de la veille) | **100 → 20,0 °C** |

Séquence : `cool` → `set_temperature 20` → `heat`, sans toucher à la consigne de chaud. L'anomalie signalée par le développeur est corrigée.

## Relevés

| Relevé | Heure | Mode | Filtration | Compresseur | `discrete` à 1 | Codes |
|---|---|---|---|---|---|---|
| S0 consignes remises | 10:33:52 | heat | on | 0 % | 0, 2, 3, **4**, 5, 6, 8 | — |
| E1 PAC éteinte, filtration on | 10:34:09 | off | on | 0 % | 2, 3, **4**, 5, 6, 8 | — |
| E2 filtration coupée + 20 s | 10:34:31 | off | off | 0 % | 2, 3, 5, 6, 16, 51 | E3 |
| E3 filtration coupée + 90 s | 10:35:41 | off | off | 0 % | 2, 3, 5, 6, 16, 51 | E3 |
| E4 retour du débit + 20 s | 10:36:01 | off | on | 0 % | 2, 3, **4**, 5, 6 | — |

Détail complémentaire : `coil` = 0, 16, 32 en S0 (PAC allumée en chaud), puis vide dès que la PAC est éteinte.

## Réponse à la question

**Oui. DIN3 suit le débit d'eau indépendamment de l'état de la PAC.**

- PAC éteinte et filtration en marche : `discrete 4` = **1** (E1, E4).
- Filtration coupée : `discrete 4` = **0** en moins de **20 s** (E2), et reste à 0 à 90 s (E3).
- Retour de la filtration : `discrete 4` revient à **1** en moins de **20 s** (E4).

Un capteur binaire « débit d'eau » sur l'entrée 4 est donc utilisable en permanence, y compris PAC à l'arrêt — c'est la seule entrée du bus qui reste fiable dans cet état.

## Autres observations

- **`discrete 8` (OUT2)** suit aussi le débit, mais avec un retard plus long que 20 s : il est à 0 en E2 et E3, et n'est pas encore revenu à 1 vingt secondes après le retour du débit (E4). Il était revenu plus tard lors de l'essai A. Ce comportement reste compatible avec une sortie de commande de pompe (P0), pas avec une vanne 4 voies.
- **`discrete 16` et `discrete 51`** passent à 1 uniquement quand le débit manque (E2, E3) et retombent à 0 dès le retour du débit (E4). 51 est cohérent avec le défaut E3 ; 16 pourrait être l'agrégat « défaut actif ».
- **E3 apparaît et disparaît en moins de 20 s** : le délai de 45 s observé la veille venait bien du rafraîchissement des entités Home Assistant toutes les 30 s, comme l'a expliqué le développeur.
- Les `coil` 0, 16 et 32 ne sont à 1 que PAC en marche : ce sont des bits de commande, pas des témoins de débit.

## État final

- PAC éteinte (`climate` = off), puis alimentation coupée 30 s plus tard : relais `switch.prise_pac_piscine` à `off`, 0 W, les 30 entités `fairland` repassent en `unavailable`.
- Filtration laissée en marche, comme trouvée.
- Consigne de froid laissée à 20,0 °C (`holding 4` = 100), consigne de chaud à 28,0 °C (`holding 3` = 116), préréglage `silence`.

## Fichiers

- `diag-E-S0-consignes-remises.json`
- `diag-E-E1-PAC-off-filtration-on.json`
- `diag-E-E2-filtration-coupee-20s.json`
- `diag-E-E3-filtration-coupee-90s.json`
- `diag-E-E4-retour-debit-20s.json`
- `essai-E.json` (synthèse des cinq relevés, tableau JSON)
- `journal-essai-E.txt` (journal d'exécution horodaté)

Les diagnostics sont réduits au bloc `data`, comme pour la campagne précédente.
