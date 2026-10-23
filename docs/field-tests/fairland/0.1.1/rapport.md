# Test de l'intégration Fairland 0.1.1 — retour terrain

**Installation** : 0.1.1 posée par-dessus la 0.1.0 (sauvegarde de la 0.1.0 faite avant), HA redémarré en 66 s, entrée de configuration conservée, aucune erreur au journal.
**Lien** : passerelle Modbus TCP, port 4196, adresse Modbus 1. HA 2026.10.2.
**Contexte** : PAC hivernée, eau 13,5 à 15 °C, air 15 à 18 °C.

## Les cinq points du guide 0.1.1

### 1. Turbo puis Super silence — **corrigé**

| Préréglage | Résultat |
|---|---|
| `turbo` | **HTTP 500** + message explicite, préréglage resté sur `silence` |
| `super_silence` | **HTTP 500** + message explicite, préréglage resté sur `silence` |
| `silence` | accepté (200) |
| `smart` | accepté (200) quand le compresseur tourne |

Message renvoyé : « The heat pump did not switch to this preset. Some models do not have every working mode, and some accept Smart only while the compressor runs ». C'est exactement le comportement attendu : avant, l'appel répondait 200 et rien ne changeait.

Détail à vérifier de ton côté : ce message sort **en anglais** par l'API REST alors que la traduction française existe dans `translations/fr.json` (`exceptions.preset_refused`). À confirmer à l'écran, l'interface traduit peut-être correctement.

### 2. Smart compresseur arrêté puis en marche — **confirmé**

- compresseur arrêté (0 %, 0 A) : `smart` → **refusé**, HTTP 500, message explicite, préréglage resté sur `silence`
- compresseur en marche (52 %) : `smart` → **accepté**, relu `smart`

Le délai de démarrage du compresseur après passage en chauffage est d'environ **2 minutes 15** (135 s), deux fois de suite. Ensuite la montée est franche : 28 % → 42 % → 52 % → 75 %.

### 3. Absence de débit d'eau — **corrigé et sans ambiguïté**

| Situation | `binary_sensor.…_absence_de_debit_d_eau` |
|---|---|
| Filtration en marche | `off` |
| Filtration coupée | `on` |

Le renommage règle la confusion de la 0.1.0. Reste l'ancienne entité `binary_sensor.…_debit_d_eau`, désormais `unavailable` : elle peut être supprimée du registre, je ne l'ai pas fait.

### 4. Entités désactivées — **16 sur 30, toutes activées, valeurs plausibles**

Les 16 entités ont été activées une par une depuis le registre (même effet que « + N entités non affichées »). Après 75 s d'attente, **toutes remontent une valeur** :

| Entité | Valeur | Commentaire |
|---|---|---|
| Température d'aspiration | 13,0 °C | cohérent avec l'eau à 14,5 et l'air à 14,5 |
| Température de l'échangeur | 15,0 °C | cohérent |
| Température de l'évaporateur | 10,5 °C | plausible, compresseur arrêté |
| Température de refoulement | 17,5 °C | plausible |
| Température du dissipateur | 19,5 °C | plausible |
| Fréquence compresseur | 0 Hz | compresseur arrêté, normal |
| Fréquence cible | 0 Hz | idem |
| Ouverture du détendeur | 480 | valeur stable, à confirmer en marche |
| Vitesse du ventilateur | 0 rpm | compresseur arrêté |
| Tension PFC | 317 V | plausible |
| Contact de commande à distance | on | |

**Réglages P1 à P5, tous relus :**

- Durée de mesure de la pompe : **60 min**
- Durée de fonctionnement avant dégivrage : **35 min**
- Durée maximale de dégivrage : **12 min**
- Température de début de dégivrage : **−7,0 °C**
- Température de fin de dégivrage : **13,0 °C**

Ces cinq valeurs sont cohérentes entre elles et avec un réglage usine. Je n'ai pas accès au menu installateur de la PAC pour les comparer une à une — à faire de ton côté si tu veux la confirmation.

### 5. Diagnostic juste après un dégivrage — **aucun bit ne bouge**

Trois diagnostics pris dans la foulée de l'appui sur « Lancer un dégivrage » : avant, à 3 s, à 30 s.

| Relevé | Codes actifs | Bobines à 1 | Entrées discrètes à 1 |
|---|---|---|---|
| avant | aucun | 0, 16, 32 | 0, 2, 3, 4, 5, 6, 8, 17 |
| après 3 s | aucun | 0, 16, 32 | 0, 2, 3, 4, 5, 6, 8, 17 |
| après 30 s | aucun | 0, 16, 32 | 0, 2, 3, 4, 5, 6, 8, 17 |

**Aucune bobine ni entrée discrète ne change** : pas un seul bit ne bascule, ni à 3 s ni à 30 s, et le compresseur continue sa route (75 %) sans interruption. Si la carte mémorisait la demande, on s'attendrait à voir un bit apparaître puis retomber — il n'y en a aucun.

Les seules valeurs qui évoluent sont des registres analogiques d'entrée, et elles évoluent comme le reste de la machine qui tourne :

- à 3 s : `input.6` 42 → 43, `input.14` 629 → 632
- à 30 s : `input.0` 58 → 79, `input.6` 42 → 46, `input.10` 50 → 66, `input.14` 629 → 662, plus quelques voisins de ±1 ou ±2

Rien de spécifique au dégivrage là-dedans. Conclusion : soit la carte ignore la demande quand elle ne juge pas le dégivrage nécessaire, soit le témoin de demande n'est pas dans le bloc interrogé par l'intégration.

## Tests complémentaires

**Modes et consignes** — `heat`, `cool`, `heat_cool` acceptés et relus ; consigne modifiable dans chaque mode (20 en froid, 26 en auto, 28 en chaud). Compresseur suit le mode choisi.

**Défaut E3** — filtration coupée alors que la machine était en chauffage : `sensor.…_defaut` passe à **`e3`** à t+45 s, `absence_de_debit_d_eau` passe à `on` au même instant, défaut réarmé tout seul ensuite. Toujours aussi net.

**Températures** — eau entrée 14,5 °C / sortie 14,5 °C à l'arrêt, 14,5 → 17,0 °C après un cycle de chauffe, air 14,5 à 18 °C selon les moments.

## État laissé après les tests

PAC **éteinte**, filtration **coupée**, compresseur à 0 %, aucune écriture hors des tests listés. Le défaut E3 est affiché tant que la filtration ne tourne pas — c'est le comportement normal de la carte, il disparaît au redémarrage de la pompe.

## Toujours en attente de ta part

- Marque et modèle de la passerelle Modbus TCP
- Référence imprimée sur la carte électronique (MWH216, MWH298, autre)
