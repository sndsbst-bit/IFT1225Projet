# IFT1225Projet
# Boussole — plateforme de planification des études

> IFT2255 Génie logiciel · Automne 2026 · Projet de session, phase 1
> Release évaluée : `v1.0-phase1` (2 octobre 2026)

## 1. À quoi sert le projet

Boussole aide une personne étudiante à planifier sa session **avant** de s'inscrire. Elle rassemble en un seul endroit les cours, les projets supervisés, les postes en laboratoire, les stages et les activités. Elle relie cette offre au programme et au dossier de la personne, et vérifie à chaque ajout les règles qui coûtent cher quand on les découvre trop tard : préalables, conflits d'horaire, plafond de crédits, seuil de temps plein, dates limites. Elle suit aussi les demandes adressées aux personnes qui encadrent, avec des délais visibles.

Ce dépôt contient le **prototype** de notre solution et les **sources des diagrammes** du rapport de phase 1. Le prototype ne couvre pas toutes les fonctions : il sert à rendre nos décisions de conception observables.

## 2. État d'avancement

### Ce qui fonctionne

| Fonction | Exigence du rapport |
|---|---|
| Offre de la session (cours, projets supervisés, activités) avec filtre de recherche | EX-14 |
| Refus de l'ajout d'un cours dont un préalable n'est pas réussi, avec le préalable nommé | EX-03 |
| Refus d'un cours complet, avec proposition de cours ouverts du même bloc | EX-07 |
| Refus au-delà du plafond de crédits, et de tout ajout après la date limite de modification | EX-09 (partiel) |
| Avertissement pour un cours hors programme, qui ne compte dans aucun bloc | EX-05 |
| État de temps plein visible en permanence, et confirmation du plan bloquée tant que la conséquence du temps partiel n'est pas acceptée | EX-08 |
| Progression par bloc qui ne compte que les éléments crédités (les activités valent 0 crédit) | EX-01, EX-06 |
| Demande de projet : vérification d'admissibilité, délai de réponse affiché, rappel à J-2, relance unique ou redirection vers des offres équivalentes, expiration visible | EX-10 |
| Indicateur agrégé de disponibilité pour chaque projet (demandes en attente, délai habituel) | EX-11 (partiel) |
| Journal de tous les événements (ajouts, refus, rappels, réponses) | — |
| 13 tests unitaires sur le moteur de règles et le cycle des demandes | — |

### Ce qui est simulé

- **Données** : l'offre, le dossier étudiant et les règles sont des fichiers JSON (`prototype/data/`). Les préalables, capacités et seuils sont **illustratifs**. Ils remplacent le service d'import et les systèmes externes (Synchro, répertoire, calendrier) du C4.
- **Back-end** : aucun serveur applicatif ni base de données. `api.js` joue le rôle de l'API et garde l'état en mémoire ; `regles.js` joue le rôle du moteur de règles. Recharger la page remet tout à zéro.
- **Temps** : le bouton « Avancer d'un jour » remplace l'ordonnanceur (délais, rappels, expirations).
- **Réponses des encadrant·es** : fixées dans `offre.json` (`reponseSimulee`). Par exemple, Prof. Lavoie accepte après 3 jours et Prof. Okonkwo ne répond jamais.
- **Approbation du conseil de programme** et **inscription dans Synchro** : considérées comme acquises.
- **Authentification** : aucune ; un profil fictif de 2ᵉ année (30 crédits acquis) est chargé.

### Ce qui reste à faire (phases suivantes)

- API Java / Spring Boot et base de données PostgreSQL (C4 niveau 2).
- Import réel du répertoire, du calendrier et du dossier, avec consentement (EX-02).
- Horaires, sections et conflits d'horaire (EX-04).
- Rappels d'échéance par courriel et abandon avec frais (EX-09 complet).
- Processus complet du projet supervisé : entente et approbation réelle (EX-12).
- Vue multi-sessions (EX-13) et repères partagés (EX-15).
- Tests de l'interface.

## 3. Installer et lancer le prototype

**Prérequis :** un navigateur récent et Python 3. Aucune dépendance à installer.

```bash
git clone https://github.com/[À COMPLÉTER]/[À COMPLÉTER].git
cd [À COMPLÉTER]/prototype
python3 -m http.server 8000
```

Ouvrez ensuite **http://localhost:8000**.

> Le serveur local est nécessaire : les navigateurs bloquent la lecture des fichiers JSON quand on ouvre `index.html` par un double-clic.

**Lancer les tests** (Node.js 20 ou plus récent), depuis la racine du dépôt :

```bash
node --test tests/*.test.mjs
```

### Scénario de démonstration (3 minutes)

1. **Préalable manquant (EX-03)** : dans l'onglet *Cours*, cliquez *Ajouter* sur **IFT3395**. L'ajout est refusé et le préalable IFT2015 est nommé.
2. **Hors programme (EX-05)** : ajoutez **IFT2015**, puis **FINA10200**. Le second est ajouté avec un avertissement : il ne compte dans aucun bloc.
3. **Temps plein (EX-08)** : avec 6 crédits, l'encadré orange indique le temps partiel et sa conséquence. Cliquez *Confirmer le plan* : une fenêtre exige d'accepter la conséquence avant de confirmer.
4. **Délai d'une demande (EX-10)** : dans l'onglet *Projets supervisés*, essayez d'abord le projet de Prof. Bhattacharya (refusé : 60 crédits requis). Envoyez ensuite une demande à **Prof. Okonkwo** (9 demandes en attente, délai habituel de 12 jours). Cliquez 5 fois sur *Avancer d'un jour* : le rappel apparaît avec les boutons *Relancer* et *Choisir une autre offre*.
5. **Redirection** : cliquez *Choisir une autre offre*, envoyez une demande à **Prof. Lavoie**, avancez de 3 jours, puis *Accepter l'entente*. Le projet compte maintenant dans les crédits.

### Régénérer les diagrammes

Les sources PlantUML sont dans `docs/diagrammes/`. Il faut Java et [plantuml.jar](https://plantuml.com/download) :

```bash
cd docs/diagrammes
java -jar plantuml.jar -tpng *.puml
```

### Organisation du dépôt

```
.
├── README.md
├── prototype/
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── app.js        # interface (« Application web » du C4)
│   │   ├── api.js        # API simulée, état en mémoire
│   │   ├── regles.js     # moteur de règles (fonctions pures)
│   │   └── demandes.js   # cycle de vie des demandes (fonctions pures)
│   └── data/             # offre.json, dossier.json, regles.json
├── tests/
│   └── regles.test.mjs   # tests unitaires (node --test)
└── docs/
    ├── rapport/          # Rapport_Phase1_IFT2255.pdf
    ├── diagrammes/       # sources .puml + images (A1, A2, A3)
    └── traces/           # sessions exportées du prototype de référence
```

## 4. Équipe et répartition du travail

| Membre | Matricule | Contribution principale |
|---|---|---|
| Soundous Bestam | 20304594 | |
| Ahmed Nassim Es-Snoussi | 20320830 |  |
| Victorio Nascimento | 20299568 |  |


Toutes les personnes de l'équipe ont relu le rapport.

## 5. Outils d'assistance logicielle



| Outil | Utilisé pour | Ce que l'équipe a fait |
|---|---|---|
| Claude (Anthropic) | Explication de l'énoncé ; analyse comparative des trois sessions exportées ; première version des simplifications, des exigences, des fiches de cas d'utilisation et du rapport ; sources PlantUML des diagrammes A1, A2 et A3 ; première version du code du prototype et des tests ; ce README. | Relecture et compréhension du code du prototype, vérification des observations dans le prototype, vérification des règles de l'Université, relecture et correction de l'ensemble. |
| PlantUML | Rendu des diagrammes (cas d'utilisation, activités, C4-PlantUML). | Sources versées dans `docs/diagrammes/`. |
