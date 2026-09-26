# Modèle du domaine (base des modèles Django)

Diagramme : `diagrammes/domaine.puml`.

## Entités

| Entité | Rôle | Attributs clés |
|---|---|---|
| Personne | Compte avec rôle (étudiante, encadrante, conseil) | nom, rôle |
| Profil | Intérêts et préférences d'une personne étudiante | intérêts, crédits visés, préférence d'apprentissage, programme |
| Programme | Ensemble de règles | nom, cycle |
| Regle | Exigence de programme, donnée modifiable | type (minimum, plafond, bloc, temps plein), valeur, portée |
| Activite | Offre générique | type, titre, crédits, places, source, mise à jour |
| Cours, Projet, Poste, Stage, Seminaire, Concours | Spécialisations d'Activite | préalables, horaire, échéance, hôte |
| Hote | Superviseur, laboratoire ou organisation | type, capacité, disponibilité (estimée) |
| Session | Une session, courante selon la date réelle | libellé, date de début et de fin |
| Echeance | Date limite officielle | session, libellé, date, abandon (oui ou non) |
| Element | Case du plan d'une personne pour une session (le Plan est l'ensemble de ses éléments, plus de table Plan) | personne, session, activité, état |
| Demande | Demande à un hôte | élément, état, date d'expiration |
| Appreciation | Retour sur une activité suivie | activité, note |

## États importants

- **Element** : `vide`, `demande`, `offert`, `confirme`, `intention`, `retire`.
  `intention` n'occupe aucune place (E-16).
- **Demande** : `envoyee`, `acceptee`, `refusee`, `expiree`.
- **Etat de regle** (calculé, jamais stocké) : `respectee`, `a_risque`, `violee`.

## Règles métier à coder

1. Un élément `confirme` compte dans les crédits ; un élément `intention` n'y compte pas.
2. Une demande dont `date_expiration` antérieure à la date du jour passe à `expiree`
   (date réelle, évaluée à chaque requête).
3. Chaque règle est évaluée sur le plan et retourne un état et un message.
4. Toute disponibilité d'hôte est affichée avec la mention « estimation » (E-12).
