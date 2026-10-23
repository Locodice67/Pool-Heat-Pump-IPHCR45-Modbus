# Tests terrain — intégration Fairland (PAC piscine GEPAC08)

Campagnes de test menées sur une vraie PAC Fairland **GEPAC08** pour l'intégration
`fairland` en cours de développement (proposition d'intégration Core commune, voir
l'issue #2 de ce dépôt).

Matériel et environnement :

- Home Assistant 2026.10.2
- passerelle Modbus TCP, port **4196**, adresse Modbus **1**
- PAC hivernée : eau entre 13,0 et 15,0 °C, air entre 8,0 et 18,0 °C
- les tests sont faits sur l'eau du bassin, filtration pilotée à distance

Voir **[SYNTHESE.md](SYNTHESE.md)** pour le tableau « ce qui marche / ce qui ne marche pas » version par version.

Un dossier par version testée. Chaque dossier contient le rapport de la campagne et
les diagnostics de l'entrée de configuration (bloc `data` seul : les blocs
`home_assistant` et `custom_components` ont été retirés, ils ne contiennent rien
d'utile au diagnostic et listent l'installation complète).

## Journal des versions

| Version | Date | Résultat principal |
|---|---|---|
| 0.1.0 | 2026-10-23 | modes, consignes et défaut E3 OK ; préréglages refusés silencieusement, débit d'eau inversé, 12 entités vides |
| 0.1.1 | 2026-10-23 | les cinq points du guide sont traités : erreur explicite sur préréglage refusé, absence de débit cohérente, entités désactivées renseignées |
| 0.1.1b | 2026-10-23 | 2ᵉ campagne sur la 0.1.1 : essais A à D (contrôleur de débit, OUT2, courant, interface) → [dossier](0.1.1b/rapport.md) |
