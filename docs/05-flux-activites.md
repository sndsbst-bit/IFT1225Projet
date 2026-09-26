# A2 : Cinq flux principaux (brouillon)

Sources : `diagrammes/flux*.puml`. Les couloirs séparent personne étudiante, système et
acteurs externes. Colonne « Écart avec le prototype » : **hypothèse à confirmer** par la
manipulation (semaine 1) avant de la reprendre dans le rapport.

| Flux | Cas | Particularité exigée | Exigences | Écart supposé avec le prototype (à confirmer) |
|---|---|---|---|---|
| F1 Ajout d'une activité | CU3, CU4 | Points de décision, fin en échec (règle violée) | E-05 à E-08 | Prototype sans conflit d'horaire ni préalable (S1, S2) |
| F2 Demande d'encadrement | CU5, CU6 | **Dépend d'un tiers**, **soumis à une échéance** (expiration) | E-10, E-11, E-12 | Réponse et expiration moins nuancées (S7, S8) |
| F3 Validation au registrariat | CU9 | **Fin en échec** (rejet), dépend d'un tiers | E-07, E-16 | Registrariat simulé, rejet probablement absent |
| F4 Échéance et abandon | CU7 | **Soumis à une échéance** (date limite d'abandon) | E-09 | Dates génériques (S4) |
| F5 Projection multi-sessions | CU8 | Chemin alternatif (activité non offerte) | E-13, E-14, E-16 | Toutes sessions supposées offertes (S6), intention vs place (S14) |

Couverture de l'énoncé : au moins un flux qui échoue (F1, F3), un qui dépend d'un tiers
(F2, F3), un soumis à une échéance (F2, F4).

## Texte court par flux

À rédiger après observation. Gabarit : « Le prototype fait X. Le système visé fait Y parce
que Z (observation, source). »
