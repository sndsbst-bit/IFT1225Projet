# A1 : Cas d'utilisation (brouillon)

Diagramme : `diagrammes/cas-utilisation.puml`.

## Acteurs

| Type | Acteur |
|---|---|
| Principal | Personne étudiante |
| Secondaire | Personne qui encadre (superviseur, laboratoire, organisation), Conseil de programme |
| Systèmes externes | Registrariat (inscription), Répertoire des cours, Calendrier officiel |

## Liste des cas

| ID | Cas | Acteur | Exigences |
|---|---|---|---|
| CU1 | Gérer son profil et ses exigences | Étudiante | E-03 |
| CU2 | Explorer le catalogue d'offres | Étudiante | E-01, E-02, E-04 |
| CU3 | Ajouter une activité au plan | Étudiante | E-05 à E-08 |
| CU4 | Vérifier les règles du programme | Étudiante | E-05, E-06, E-07 |
| CU5 | Demander une place de projet ou de stage | Étudiante, Encadrante | E-10, E-12 |
| CU6 | Répondre à une demande | Encadrante | E-10, E-11 |
| CU7 | Suivre les échéances | Étudiante | E-09 |
| CU8 | Projeter plusieurs sessions | Étudiante | E-13, E-14, E-16 |
| CU9 | Valider le plan auprès du registrariat | Étudiante, Registrariat | E-07, E-16 |
| CU10 | Donner une appréciation | Étudiante | E-04 |
| CU11 | Maintenir les règles du programme (hors fiches principales) | Conseil de programme | N-02 |

Relations : CU3 **inclut** CU4. CU3 est **étendu** par « Voir les alternatives » quand
une règle est violée. CU5 **inclut** « Afficher la disponibilité estimée ». CU7 consulte le
Calendrier officiel. CU2 consulte le Répertoire des cours.

## Fiches (dix cas principaux)

Format : but (du point de vue de l'acteur), déclencheur, préconditions, postconditions
(succès / échec), dépendances.

**CU1 Gérer son profil**
- But : que le système comprenne ce que je veux apprendre.
- Déclencheur : première visite ou changement de projet.
- Pré : personne connectée .
- Post succès : profil enregistré, suggestions recalculées. Échec : profil inchangé, erreurs affichées.
- Dépendances : alimente CU2 et CU4.

**CU2 Explorer le catalogue**
- But : voir toute l'offre au même endroit.
- Déclencheur : début de planification.
- Pré : catalogue chargé pour la session.
- Post succès : liste filtrée avec source, places et mise à jour. Échec : message « données indisponibles », catalogue précédent affiché avec sa date.
- Dépendances : Répertoire des cours.

**CU3 Ajouter une activité au plan**
- But : décider en connaissant les conséquences.
- Déclencheur : clic sur « ajouter ».
- Pré : activité visible, plan existant.
- Post succès : élément ajouté (état `offert` ou `intention`), règles recalculées. Échec : plan inchangé, règles violées listées.
- Dépendances : inclut CU4.

**CU4 Vérifier les règles**
- But : savoir ce qui bloque avant de confirmer.
- Déclencheur : tout changement du plan.
- Pré : règles du programme disponibles.
- Post succès : un état par règle. Échec : état « non évalué » avec raison.
- Dépendances : Programme (règles).

**CU5 Demander une place**
- But : obtenir une réponse sans épuiser mes chances.
- Déclencheur : choix d'un projet ou d'un stage.
- Pré : place possible, capacité de la personne encadrante non nulle.
- Post succès : demande `envoyee` avec date d'expiration. Échec : refus immédiat avec raison (capacité, délai).
- Dépendances : CU6, Hôte.

**CU6 Répondre à une demande**
- But : dire non tôt, accepter de façon soutenable.
- Déclencheur : demande reçue.
- Pré : demande `envoyee` non expirée.
- Post succès : `acceptee` ou `refusee`, capacité ajustée. Échec (expirée) : `expiree`, étudiante notifiée.
- Dépendances : CU5.

**CU7 Suivre les échéances**
- But : ne rien rater.
- Déclencheur : ouverture de la page, changement de date.
- Pré : calendrier de session chargé.
- Post succès : échéances proches en alerte. Échec : calendrier absent, dernière version datée affichée.
- Dépendances : Calendrier officiel.

**CU8 Projeter plusieurs sessions**
- But : voir les conséquences à deux sessions.
- Déclencheur : ouverture de la vue multi-sessions.
- Pré : au moins un plan.
- Post succès : projection, intentions distinguées des places. Échec : sessions non offertes signalées.
- Dépendances : CU3, CU4.

**CU9 Valider le plan auprès du registrariat**
- But : inscription valide.
- Déclencheur : clic sur « soumettre ».
- Pré : aucune règle violée.
- Post succès : éléments `confirme`. Échec : rejet avec motif, éléments inchangés.
- Dépendances : Registrariat (`TEMP(registrariat)`: simulé).

**CU10 Donner une appréciation**
- But : améliorer les suggestions.
- Déclencheur : fin de session.
- Pré : activité suivie.
- Post succès : appréciation enregistrée. Échec : sans effet.
- Dépendances : CU2 (suggestions).
