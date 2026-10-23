# Synthèse des campagnes — intégration Fairland sur GEPAC08

Deux versions testées le **2026-10-23** sur la même PAC, dans les mêmes conditions
(HA 2026.10.2, passerelle Modbus TCP port 4196, adresse 1, PAC hivernée eau 13-15 °C).

| Version | Archive | Mise en service | Campagne |
|---|---|---|---|
| 0.1.0 | `fairland-test-gepac08.zip` | 08:26 | matin, 4 séries de tests |
| 0.1.1 | `fairland-test-gepac08-0.1.1.zip` | 11:42 | après-midi, les 5 points du guide |

## Ce qui a marché

| Fonction | 0.1.0 | 0.1.1 |
|---|---|---|
| Installation et chargement (29 puis 30 entités, aucune erreur) | OK | OK |
| Températures eau entrée / sortie et air ambiant | OK | OK |
| Mode chauffage, froid et auto : écriture et relecture | OK | OK |
| Consigne modifiable dans chaque mode (20 / 26 / 28 °C) | OK | OK |
| Démarrage compresseur après passage en chauffe | OK (~3 min) | OK (~2 min 15) |
| Montée en régime du compresseur | 30 → 100 %, 1,8 A | 28 → 42 → 52 → 75 % |
| Préréglage `silence` | OK | OK |
| Préréglage `smart` compresseur en marche | OK | OK |
| Défaut E3 sur perte de débit (apparition à t+45 s) | OK | OK |
| Diagnostic de l'entrée de configuration | OK | OK |

## Ce qui n'a pas marché

| Fonction | 0.1.0 | 0.1.1 |
|---|---|---|
| Préréglage `turbo` | REFUSÉ sans aucun message | REFUSÉ, erreur explicite (corrigé côté information) |
| Préréglage `super_silence` | REFUSÉ sans aucun message | REFUSÉ, erreur explicite (corrigé côté information) |
| Préréglage `smart` compresseur arrêté | REFUSÉ sans aucun message | REFUSÉ, erreur explicite |
| Bouton « Lancer un dégivrage » | sans effet, aucun bit ne bouge | sans effet, aucun bit ne bouge |
| Débit d'eau | inversé (OFF avec filtration en marche) | corrigé et renommé `absence_de_debit_d_eau` |
| Entités diagnostic (12 d'entre elles) | restaient à `none` | renseignées après activation |
| Réglages P1 à P5 | à `none` | lus et cohérents |

## Ce qui reste ouvert

- **Dégivrage** : le bouton ne produit aucun changement observable, ni dans les
  bobines, ni dans les entrées TOR, avant / +3 s / +30 s après l'appui, et le
  compresseur n'est pas interrompu. Soit la carte ignore la demande hors conditions
  de givre, soit le témoin de demande n'est pas dans le bloc interrogé.
- **`turbo` et `super_silence`** : refusés par la carte elle-même (le super silence
  n'a jamais pu être activé sur cette machine, même avec le fork d'un tiers). La
  0.1.1 le dit maintenant clairement, mais la fonction reste indisponible.
- **Message d'erreur en anglais** par l'API REST alors que la traduction française
  existe dans `translations/fr.json` — à confirmer dans l'interface.
- **Comparaison P1 à P5** avec le menu installateur de la PAC : non faite, pas d'accès.
- **Passerelle et carte** : marque et modèle de la passerelle Modbus TCP, et
  référence imprimée sur la carte électronique (MWH216, MWH298, autre) — inconnus.

## Détail des campagnes

- `0.1.0/rapport.md` et `0.1.0/diagnostic.json`
- `0.1.1/rapport.md`, les deux journaux de campagne et les trois diagnostics
  (avant / +3 s / +30 s après dégivrage)

## Deuxième campagne sur la 0.1.1 (essai A à E)

Campagne menée le même soir pour identifier les entrées et sorties de la carte, puis
vérifier le comportement PAC éteinte.

| Point | Résultat |
|---|---|
| Entrée de débit DIN3 (`discrete` 4) | suit le contrôleur de débit, à 0 dans les 10 s suivant la coupure et de retour dès le rétablissement |
| Sortie OUT2 (`discrete` 8) | ne suit ni le compresseur ni le mode : reste à 1 dix secondes après la coupure, tombe à 90 s, revient au débit avant redémarrage — sortie pompe probable |
| Sortie OUT6 (`discrete` 12) | ne s'allume qu'en froid : vanne 4 voies très probable |
| Mode de travail | `holding` 0 porte la fonction (0 auto, 1 chauffage, 2 froid) ; `holding` 2, 3 et 4 sont les consignes de chaque fonction |
| Courant | échelle 0,1 A cohérente si on la rapporte à la tension PFC ; l'écart apparent venait de la consommation de la PAC à l'arrêt et du point de mesure côté secteur |
| Message de préréglage refusé | en français dans l'interface, en anglais par l'API REST (normal) |

Détail dans `0.1.1b/rapport.md`.
