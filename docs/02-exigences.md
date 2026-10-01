# Exigences du système visé

Priorité : **M** (doit), **S** (devrait), **C** (peut). Colonne « Observation » : le
constat (prototype, conseiller, tiers) qui justifie l'exigence. **À remplir avant le rapport.**

| ID | Exigence | Obj. | Prio | Simpl. | Observation |
|---|---|---|---|---|---|
| E-01 | Le système affiche cours, projets, postes, stages, séminaires et concours dans un même catalogue filtrable par type | O1 | M | | À faire |
| E-02 | Chaque offre indique sa source, sa date de mise à jour et ses places restantes | O1 | S | S9 | À faire |
| E-03 | La personne déclare ses intérêts, ses crédits visés et sa préférence d'apprentissage | O2 | M | | À faire |
| E-04 | Le système classe les offres selon le profil et explique pourquoi une offre est suggérée | O2 | S | S10 | À faire |
| E-05 | Les exigences du programme (blocs, minimums, plafonds) sont évaluées sur le plan courant, une règle à la fois | O3 | M | S3 | À faire |
| E-06 | Chaque règle a un état visible (respectée, à risque, violée) **avant** la confirmation d'un ajout | O3 | M | S3 | À faire |
| E-07 | Le système détecte les conflits d'horaire et les préalables manquants | O3 | M | S1, S2 | À faire |
| E-08 | Le seuil de temps plein est affiché avec sa conséquence (prêts, bourses) | O3 | M | S3 | À faire |
| E-09 | Les dates limites de la session sont visibles et une échéance proche génère une alerte | O4 | M | S4 | À faire |
| E-10 | Une demande à une personne qui encadre a un état (envoyée, acceptée, refusée, expirée) et une date d'expiration | O4 | M | S7 | À faire |
| E-11 | La personne qui encadre voit ses demandes, peut refuser tôt et fixer une capacité | O4, O6 | S | S8, S12 | À faire |
| E-12 | Toute donnée incertaine (disponibilité, place, délai) est présentée comme estimation | O6 | M | S8 | À faire |
| E-13 | Un plan projette plusieurs sessions et distingue **intention** et **place confirmée** | O5 | M | S14 | À faire |
| E-14 | Les activités n'étant offertes que certaines sessions sont signalées en projection | O5 | S | S6 | À faire |
| E-15 | Les informations de tradition orale ayant une réponse connue (délais typiques, réponses fréquentes) sont consultables | O6 | C | | À faire |
| E-16 | Aucune action du système ne présente une intention comme une inscription | O5 | M | S14 | À faire |

## Exigences non fonctionnelles (à valider)

| ID | Exigence | Observation |
|---|---|---|
| N-01 | Un plan est évalué en moins de deux secondes pour un profil type | À faire |
| N-02 | Chaque règle de programme est une donnée modifiable, pas du code | À faire |
| N-03 | Les données personnelles de la personne étudiante ne sont visibles que d'elle (et du conseil au besoin) | À faire |

## Portée du prototype de phase 1 (guide pour le code)

Parcours à rendre tangibles, parmi les cinq flux A2 :
1. Vérifier les règles avant d'ajouter une activité (E-05, E-06, E-07).
2. Demande à une personne qui encadre, avec expiration (E-10, E-12).
3. Projection multi-sessions avec intention vs place confirmée (E-13, E-16).

Tout le reste est marqué `TEMP`.
