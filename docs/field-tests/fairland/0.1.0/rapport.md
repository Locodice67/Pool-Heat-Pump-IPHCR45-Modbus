# Test de l'intégration Fairland 0.1.0 — retour terrain

**Installation** : PAC piscine Fairland (gérée jusqu'ici par une intégration perso `pool_heat_pump_iphcr45_modbus`, désactivée pour le test).
**Passerelle** : Modbus TCP `10.10.2.70:4196`, adresse Modbus **1**.
**Home Assistant** : 2026.10.2. Entités créées : 29. Aucune erreur dans le journal HA pendant les tests.

## 1. Températures — cohérentes

| Grandeur | Valeur lue par l'intégration |
|---|---|
| Eau entrée | 14,0 °C |
| Eau sortie | 14,5 °C |
| Air ambiant | 8,0 °C |

Le ΔT de 0,5 K avec le compresseur à 100 % est plausible, la PAC chauffe réellement l'eau.
Reste à comparer avec l'affichage de la machine (à faire).

## 2. Modes et consignes — tout fonctionne

| Mode | Passage | Consigne |
|---|---|---|
| `heat` | accepté, relu `heat` | 28 °C accepté |
| `cool` | accepté, relu `cool` | 20 °C accepté |
| `heat_cool` | accepté, relu `heat_cool` | 26 °C accepté |

La consigne se change correctement dans chaque mode (relue après écriture), et le compresseur suit : démarrage environ 3 minutes après le passage en chauffage, puis montée en régime 30 % → 56 % → 79 % → 95 % → 100 %, courant 1,8 A.

## 3. Préréglages — deux sur quatre seulement

| Préréglage | Résultat |
|---|---|
| `silence` | accepté, relu |
| `smart` | accepté, relu — **mais uniquement compresseur en marche** ; refusé (silencieusement) quand le compresseur est à l'arrêt |
| `super_silence` | **refusé** à chaque essai (relu reste `silence`) |
| `turbo` | **refusé** à chaque essai (relu reste `silence`) |

Point important pour le développement : quand un préréglage est refusé, **aucune erreur n'est remontée** — l'appel de service répond 200, rien dans le journal, et la valeur ne change pas. Impossible pour l'utilisateur de savoir si le réglage a été pris ou refusé. Testé deux fois par préréglage, compresseur à l'arrêt puis en marche.

## 4. Bouton « Lancer un dégivrage » — sans effet visible

Pressé deux fois, réponse 200, l'état du bouton enregistre bien l'appui (horodatage mis à jour).

- `binary_sensor.…_degivrage` reste `off` pendant 90 s
- compresseur à 100 % pendant toute la durée d'observation, aucune variation de régime
- aucune erreur, aucun message

À noter : température ambiante 8 °C, échangeur à 14 °C — la carte refuse peut-être un dégivrage hors conditions (pas de givre). Mais là encore, si la carte refuse, il faudrait un retour explicite côté intégration.

## 5. Défaut E3 avec filtration arrêtée — **fonctionne**

Test réalisé filtration coupée, compresseur en marche à 100 % avant la coupure :

- t+15 s et t+30 s : aucun défaut
- **t+45 s : `sensor.…_defaut` passe à `e3`, `binary_sensor.…_defaut` à `on`**, compresseur arrêté immédiatement
- le défaut reste affiché environ 3 minutes, puis se réarme seul à t+225 s

Le capteur de défaut est donc à la fois réactif et correctement décodé (`e3` en clair, pas un code numérique).

## 6. Deux anomalies supplémentaires

**a) `binary_sensor.…_debit_d_eau` semble inversé.**
Filtration en marche, compresseur à 100 %, eau réellement chauffée (+0,5 K stable entrée/sortie) → débit d'eau lu `off`.
Filtration arrêtée, plus aucun débit → débit d'eau lu `on`.
Les deux états sont donc l'inverse de la réalité. À vérifier sur une autre carte, mais sur celle-ci c'est net.

**b) Une douzaine d'entités restent à `none` en permanence**, même compresseur à 100 % :

- température de l'évaporateur, de l'échangeur, de refoulement, d'aspiration, du dissipateur
- fréquence du compresseur (réelle et cible), ouverture du détendeur, vitesse du ventilateur, tension PFC
- les cinq nombres de réglage (durées et températures de dégivrage, durée de mesure de la pompe)

Les températures d'eau, l'ambiant, la vitesse compresseur, le courant et le défaut remontent bien. Ça ressemble à une carte dont seule une partie de la table répond.

## Questions du test restées ouvertes

- Marque et modèle de la passerelle Modbus TCP utilisée (à relever)
- Référence imprimée sur la carte électronique (MWH216, MWH298, autre) — nécessite d'ouvrir le boîtier

## État laissé après les tests

Mode chauffage, consigne 28 °C, préréglage `silence`, filtration arrêtée volontairement pour le test E3, défaut réarmé tout seul. Aucune écriture hors des tests listés ci-dessus, intégration d'origine désactivée mais toujours installée.
