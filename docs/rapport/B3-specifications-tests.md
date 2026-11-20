# 5. B3 : Spécifications de tests

Cette section précise comment on vérifiera que Boussole respecte ses 17 exigences. Elle contient les critères d'acceptation (5.1), les jeux de données d'essai (5.2), les 25 cas de test (5.3) et un tableau de couverture (5.4). Les tests ne sont pas automatisés à cette phase. Les noms de statuts (RESPECTEE, AVERTISSEMENT, BLOQUANTE, A_VERIFIER, NON_VERIFIABLE) sont ceux de l'énumération `StatutVerdict` de l'annexe 4.

## 5.1 Critères d'acceptation

| Exigence | Critère d'acceptation vérifiable |
| --- | --- |
| EX-01 | Pour un dossier donné, chaque bloc (obligatoires, options, au choix) affiche un minimum sûr et un maximum possible en crédits, et ces valeurs changent quand un cours est ajouté au plan. |
| EX-02 | Après consentement, le profil contient les cours réussis et les crédits acquis avec la provenance IMPORTEE_SYNCHRO et la date d'import. Sans import, une saisie manuelle est possible et porte la provenance SAISIE_MANUELLE, affichée « non vérifiée ». |
| EX-03 | L'ajout d'un cours dont un préalable n'est pas réussi donne un verdict BLOQUANTE qui nomme le préalable manquant. Un préalable évalué `unknown` donne A_VERIFIER, jamais RESPECTEE. |
| EX-04 | Deux sections qui se chevauchent donnent un conflit signalé à l'ajout, et les autres sections du cours sont proposées. |
| EX-05 | Un cours hors programme donne un AVERTISSEMENT (pas un blocage), ne compte dans aucun bloc, et l'autorisation requise est affichée. |
| EX-06 | Le total de crédits et la progression ne comptent que les éléments crédités. Une activité facultative vaut 0 crédit et s'affiche à part. |
| EX-07 | Une offre encadrée dont toutes les places sont prises est refusée fermement, sauf dérogation enregistrée par la personne qui encadre. Pour un cours, un avertissement daté remplace le refus. |
| EX-08 | Sous 12 crédits, la confirmation du plan est impossible tant que la conséquence (aide financière) n'est pas acceptée. À 12 crédits, aucun avertissement n'apparaît. |
| EX-09 | Chaque échéance affiche sa conséquence. Un rappel est envoyé à J-7 et à J-2 pour les éléments du plan concernés, une seule fois chacun. |
| EX-10 | Une demande affiche son délai de réponse. Un rappel part à J-2. Une seule relance est permise, une redirection est possible avant l'échéance, et une demande sans réponse devient EXPIREE à l'échéance. |
| EX-11 | L'indicateur d'une offre contient les places restantes, les demandes en attente et le délai habituel, sans aucun nom de personne. |
| EX-12 | Une demande acceptée mène à une entente, puis à l'approbation du conseil. Aucune étape ne se saute et un refus exige un motif. |
| EX-13 | Une intention sur une session sans horaire publié est marquée « offre estimée » et n'est jamais présentée comme une place obtenue. Un préalable planifié à une session antérieure est accepté, un préalable planifié dans la même session ne l'est pas. |
| EX-14 | Une recherche combine type, domaine, session et admissibilité, et renvoie exactement les offres qui satisfont tous les filtres. |
| EX-15 | Un repère n'est visible qu'après publication par le conseil, il est affiché sans nom d'auteur et il disparaît à la fin de la deuxième session suivant sa soumission. |
| EX-16 | Un ajout qui ferait dépasser 18 crédits est refusé et le message nomme le plafond de 18. Un total de 18 crédits est accepté. |
| EX-17 | Toute donnée de Planifium affiche sa date. Si la source ne répond pas, la dernière copie est utilisée et signalée, et les règles qui en dépendent sont NON_VERIFIABLE. |

## 5.2 Jeux de données d'essai

Les jeux reprennent ceux du prototype (`prototype/data/`) afin que les résultats attendus puissent être comparés au comportement observé en phase 1. Les horaires de D3 sont fictifs mais plausibles et seront remplacés par ceux de Planifium pour A26 avant la remise.

**D1, profil de l'étudiante (session A26, du 2026-09-08)**
- Programme : baccalauréat en informatique, 90 crédits.
- Cours réussis (30 crédits) : IFT1015, IFT1025, IFT1065, IFT1215, IFT1227, MAT1400, MAT1978 (obligatoires, 21 crédits), IFT1005, STT1700 (options, 6 crédits), IFT1575 (au choix, 3 crédits).
- IFT2015 n'est pas réussi.

**D2, règles (`regles.json`)**
- Plafond de crédits : 18. Seuil de temps plein : 12.
- Date limite de modification sans frais : 2026-09-16. Date limite d'abandon : 2026-11-06.
- Délai de réponse à une demande : 7 jours. Rappel : 2 jours avant l'échéance. Prolongation d'une relance : 3 jours.

**D3, offre (extrait)**

| Sigle | Crédits | Préalables | Places | Inscrits | Section et horaire (fictif) |
| --- | --- | --- | --- | --- | --- |
| IFT2015 | 3 | IFT1025 | 40 | 31 | A26IFT2015A, mardi 13 h 30 à 15 h 30 |
| IFT2105 | 3 | IFT1065 | 60 | 41 | A : mardi 14 h 30 à 16 h 30 ; B : mercredi 9 h 30 à 11 h 30 |
| IFT2035 | 3 | IFT1025 | 45 | 20 | jeudi 9 h 30 à 11 h 30 |
| IFT2255 | 3 | IFT1025 | 40 | 40 | A26IFT2255A, lundi 13 h 30 (mise à jour Planifium : 2026-09-07) |
| IFT2245 | 3 | IFT1227, IFT2015 | 36 | 12 | vendredi 9 h 30 |
| IFT3395 | 3 | IFT2015, STT1700 | 60 | 22 | lundi 9 h 30 |
| COM1500 | 3 | aucun | 80 | 44 | mercredi 13 h 30 |
| FINA10200 | 3 | aucun, hors programme (autorisation requise) | 25 | 14 | jeudi 18 h |

**D4, offres encadrées (`offre.json`)**

| Id | Titre | Domaine | Personne qui encadre | Places | Inscrits | Crédits minimum | Réponse simulée |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Outil d'aide à la correction | Génie logiciel | Prof. Lavoie | 2 | 0 | 24 | accepte après 3 jours |
| P2 | Tolérance aux pannes | Systèmes | Prof. Okonkwo | 3 | 1 | 24 | aucune |
| P3 | Détection d'anomalies | Données et IA | Prof. Bhattacharya | 2 | 0 | 60 | refuse après 5 jours |
| P4 | Visualisation de réseaux | Systèmes | Prof. Girard | 2 | 0 | 24 | accepte après 2 jours |

Activité A2 : séminaire du DIRO sur la sécurité logicielle, 0 crédit, 60 places.

## 5.3 Cas de test

Le type est N (nominal), L (limite) ou E (échec). Sauf mention contraire, la précondition de base est D1 + D2 + D3 + D4, avec un plan de session vide et la date du 2026-09-08.

### T01 · Progression par bloc avec fourchette · EX-01 · N
- **Objectif** : vérifier que la progression affiche un minimum sûr et un maximum possible.
- **Préconditions** : D1. Planifium ne rattache pas les cours réussis aux blocs (R7).
- **Entrées** : consulter la progression, puis ajouter IFT2015 au plan.
- **Étapes** : 1. ouvrir la vue de progression ; 2. noter les trois blocs ; 3. ajouter IFT2015 ; 4. rouvrir la vue.
- **Résultat attendu** : obligatoires 21 crédits sûrs sur 51, options 6 sur 30, au choix 3 sur 9, et un maximum possible plus élevé pour chaque bloc. Après l'ajout de IFT2015, le maximum possible des obligatoires augmente de 3 crédits (cours prévu, non encore réussi) et le minimum sûr reste à 21.

### T02 · Import du dossier avec consentement · EX-02 · N
- **Objectif** : vérifier l'import et la provenance.
- **Préconditions** : Synchro simulé répond avec D1. Aucun profil encore.
- **Entrées** : consentement donné.
- **Étapes** : 1. lancer l'import ; 2. consulter le profil.
- **Résultat attendu** : 10 cours réussis, 30 crédits acquis, provenance IMPORTEE_SYNCHRO et date d'import affichée.

### T03 · Échec d'import et saisie manuelle · EX-02 · E
- **Objectif** : vérifier le repli quand Synchro est inaccessible ou que le consentement est refusé.
- **Préconditions** : Synchro ne répond pas (délai dépassé).
- **Entrées** : saisie manuelle de IFT1025 et IFT1065 comme réussis, 6 crédits.
- **Étapes** : 1. lancer l'import ; 2. constater l'échec ; 3. saisir à la main ; 4. ajouter IFT2015.
- **Résultat attendu** : message d'échec sans perte de données, profil en provenance SAISIE_MANUELLE affiché « non vérifiée ». Les verdicts qui en dépendent portent la mention « sur dossier non vérifié ». Même résultat si la personne refuse le consentement.

### T04 · Préalable manquant · EX-03 · N
- **Objectif** : vérifier le refus et le nom du préalable.
- **Préconditions** : D1 (IFT2015 non réussi, STT1700 réussi).
- **Entrées** : ajout de IFT3395.
- **Étapes** : 1. ajouter IFT3395 au plan.
- **Résultat attendu** : verdict BLOQUANTE de RegleEligibilite qui nomme IFT2015. Le cours n'est pas ajouté au plan. STT1700 n'est pas mentionné.

### T05 · Préalable évalué « unknown » · EX-03 · L
- **Objectif** : vérifier qu'une incertitude n'est jamais présentée comme satisfaite (R4, R11).
- **Préconditions** : Planifium répond `unknown` pour le préalable d'un cours dont l'exigence contient une condition manuelle (par exemple « autorisation du département »).
- **Entrées** : ajout de ce cours.
- **Étapes** : 1. ajouter le cours ; 2. lire le verdict ; 3. enregistrer le plan.
- **Résultat attendu** : verdict A_VERIFIER, texte de l'exigence affiché, ajout permis (non bloquant), jamais RESPECTEE. L'élément du plan porte la mention « à vérifier ».

### T06 · Conflit d'horaire · EX-04 · E
- **Objectif** : vérifier la détection du conflit et la proposition d'autres sections.
- **Préconditions** : plan contenant IFT2015 (mardi 13 h 30 à 15 h 30).
- **Entrées** : ajout de IFT2105 section A (mardi 14 h 30 à 16 h 30).
- **Étapes** : 1. ajouter la section A ; 2. lire le verdict.
- **Résultat attendu** : verdict BLOQUANTE de RegleConflitHoraire, rencontres en cause nommées (chevauchement de 1 h), section B (mercredi 9 h 30) proposée. L'ajout de la section B réussit.

### T07 · Cours hors programme · EX-05 · N
- **Objectif** : vérifier l'avertissement et l'autorisation requise.
- **Préconditions** : D1.
- **Entrées** : ajout de FINA10200.
- **Étapes** : 1. ajouter FINA10200 ; 2. regarder la progression.
- **Résultat attendu** : verdict AVERTISSEMENT « ne compte dans aucun bloc », autorisation du département requise affichée, ajout permis, progression par bloc inchangée.

### T08 · Activités à zéro crédit · EX-06 · N
- **Objectif** : vérifier que seuls les éléments crédités comptent.
- **Préconditions** : plan vide.
- **Entrées** : ajout de IFT2015 puis du séminaire A2 et de la visite A1.
- **Étapes** : 1. ajouter IFT2015 ; 2. ajouter A1 et A2 ; 3. lire le total et la progression.
- **Résultat attendu** : total de 3 crédits, progression inchangée par les activités, activités listées dans une section à part.

### T09 · Cours complet selon Planifium · EX-07, EX-17 · E
- **Objectif** : vérifier que, pour un cours, la capacité donne un avertissement daté et non un refus ferme (R5).
- **Préconditions** : IFT2255 à 40 sur 40, `updated_at` de Planifium au 2026-09-07.
- **Entrées** : ajout de IFT2255.
- **Étapes** : 1. ajouter IFT2255 ; 2. lire le verdict.
- **Résultat attendu** : verdict AVERTISSEMENT « complet selon les données du 2026-09-07 », ajout permis, cours de même bloc proposés (IFT2035).

### T10 · Offre encadrée pleine et dérogation · EX-07 · E
- **Objectif** : vérifier le refus ferme pour une offre dont Boussole est la source, et la dérogation.
- **Préconditions** : P1 avec 2 places et 2 demandes acceptées.
- **Entrées** : demande sur P1.
- **Étapes** : 1. envoyer la demande ; 2. lire le verdict ; 3. la personne qui encadre enregistre une dérogation ; 4. renvoyer la demande.
- **Résultat attendu** : étape 2, verdict BLOQUANTE de RegleCapaciteOffre et offres ouvertes proposées. Étape 4, demande acceptée avec la dérogation tracée dans l'historique.

### T11 · Seuil de temps plein · EX-08 · L
- **Objectif** : vérifier l'avertissement sous 12 crédits et l'absence d'avertissement à 12.
- **Préconditions** : plan vide.
- **Entrées** : plan de IFT2015 et IFT2035 (6 crédits), puis ajout de IFT2105 et COM1500 (12 crédits).
- **Étapes** : 1. tenter de confirmer à 6 crédits ; 2. accepter la conséquence ; 3. confirmer ; 4. ajouter deux cours pour atteindre 12 ; 5. confirmer.
- **Résultat attendu** : étape 1 refusée, message « il manque 6 crédits » et mention de l'aide financière. Étape 3 réussie (`consequenceTempsPartielAcceptee` vrai). Étape 5 réussie sans avertissement.

### T12 · Recherche filtrée · EX-14 · N
- **Objectif** : vérifier la combinaison de filtres.
- **Préconditions** : D1 + D4 + A2.
- **Entrées** : (a) type « projet », domaine « Systèmes », admissible ; (b) type « séminaire » ; (c) domaine « Cuisine ».
- **Étapes** : appliquer chaque recherche.
- **Résultat attendu** : (a) P2 et P4 (P3 est hors filtre) ; (b) A2 ; (c) liste vide avec le message « aucune offre ne correspond ».

### T13 · Plafond de crédits · EX-16 · L
- **Objectif** : vérifier la limite exacte du plafond.
- **Préconditions** : plan de 15 crédits (IFT2015, IFT2035, IFT2105, IFT3225, IFT2905).
- **Entrées** : ajout de COM1500, puis de FINA10200.
- **Étapes** : 1. ajouter COM1500 (total 18) ; 2. ajouter FINA10200 (total 21).
- **Résultat attendu** : étape 1 acceptée. Étape 2 BLOQUANTE de ReglePlafondCredits, message qui nomme le plafond de 18 crédits et le total de 21.

### T14 · Date limite de modification · EX-09 · L
- **Objectif** : vérifier la limite de date avec l'horloge injectée.
- **Préconditions** : `Clock` fixée au 2026-09-16, puis au 2026-09-17.
- **Entrées** : ajout de IFT2015.
- **Étapes** : 1. ajouter le cours le 2026-09-16 ; 2. refaire un autre ajout le 2026-09-17.
- **Résultat attendu** : le 16, ajout accepté. Le 17, BLOQUANTE de RegleEcheance qui indique la date limite du 2026-09-16 et sa conséquence.

### T15 · Rappels d'échéance J-7 et J-2 · EX-09 · L
- **Objectif** : vérifier les rappels, leur unicité et le ciblage.
- **Préconditions** : plan contenant IFT2015, mais pas IFT2035. Échéance d'abandon au 2026-11-06.
- **Entrées** : exécution du gestionnaire aux dates 2026-10-30, 2026-10-30 (deuxième exécution), 2026-11-04.
- **Étapes** : 1. exécuter le gestionnaire le 30 octobre ; 2. le réexécuter le même jour ; 3. l'exécuter le 4 novembre.
- **Résultat attendu** : un seul courriel J-7 (la réexécution n'en envoie pas un second), un courriel J-2 le 4 novembre. Chaque courriel nomme IFT2015, jamais IFT2035, et la conséquence de l'abandon (frais, mention au relevé).

### T16 · Délai affiché et rappel d'une demande · EX-10 · N
- **Objectif** : vérifier l'échéance et le rappel J-2.
- **Préconditions** : D4 avec P2.
- **Entrées** : demande sur P2 le 2026-09-08, `traiterDelais` exécuté le 2026-09-13.
- **Étapes** : 1. envoyer la demande ; 2. lire l'échéance ; 3. avancer l'horloge au 13 septembre ; 4. exécuter `traiterDelais`.
- **Résultat attendu** : échéance de réponse au 2026-09-15 affichée avec le délai habituel de 12 jours de P2, état ENVOYEE. Le 13 septembre, un rappel part et l'état reste ENVOYEE.

### T17 · Expiration sans réponse · EX-10 · E
- **Objectif** : vérifier l'expiration comme règle interne (R15).
- **Préconditions** : demande de T16 sans réponse ni relance.
- **Entrées** : `traiterDelais` exécuté le 2026-09-16.
- **Étapes** : 1. avancer l'horloge au 16 septembre ; 2. exécuter `traiterDelais` ; 3. consulter la demande.
- **Résultat attendu** : état EXPIREE avec le libellé « délai de réponse dépassé (règle de Boussole) », sans mention de refus officiel. La personne est notifiée et des offres équivalentes sont proposées. Aucune relance n'est plus possible.

### T18 · Relance unique · EX-10 · N
- **Objectif** : vérifier qu'une seule relance est permise.
- **Préconditions** : demande sur P2 envoyée le 2026-09-08, sans réponse.
- **Entrées** : relance le 2026-09-12, puis une seconde tentative le 2026-09-13.
- **Étapes** : 1. relancer ; 2. lire l'échéance ; 3. relancer encore.
- **Résultat attendu** : état RELANCEE, échéance repoussée au 2026-09-18 (15 + 3 jours) et `relanceUtilisee` vrai. La seconde tentative est refusée avec le message « relance déjà utilisée ».

### T19 · Redirection avant l'échéance · EX-10 · N
- **Objectif** : vérifier la redirection vers une offre équivalente, et sa limite.
- **Préconditions** : demande sur P2 envoyée le 2026-09-08, sans réponse.
- **Entrées** : redirection vers P4 le 2026-09-12 ; autre tentative le 2026-09-16 sur une demande expirée.
- **Étapes** : 1. rediriger vers P4 ; 2. avancer de 2 jours ; 3. tenter une redirection d'une demande déjà expirée.
- **Résultat attendu** : la demande d'origine est fermée (RETIREE), une nouvelle demande sur P4 est créée avec sa propre échéance, et P4 répond « accepte » après 2 jours. La redirection d'une demande EXPIREE est refusée.

### T20 · Indicateur de disponibilité · EX-11 · N
- **Objectif** : vérifier le calcul et l'absence de données personnelles.
- **Préconditions** : P2 (3 places, 1 acceptée, 9 demandes en attente). Cinq dernières demandes traitées avec des délais de 2, 3, 3, 6 et 9 jours. P4 sans demande traitée.
- **Entrées** : consultation de P2 puis de P4.
- **Étapes** : 1. consulter l'indicateur de P2 ; 2. consulter celui de P4 ; 3. inspecter la réponse JSON.
- **Résultat attendu** : P2 affiche 2 places restantes, 9 demandes en attente, délai habituel de 3 jours (médiane). P4 affiche « pas encore de délai habituel ». Aucun nom ni identifiant de personne dans la réponse.

### T21 · Processus de projet supervisé · EX-12 · N
- **Objectif** : vérifier l'enchaînement demande, entente et approbation.
- **Préconditions** : D1 avec 30 crédits acquis, P1 ouvert.
- **Entrées** : demande sur P1, acceptation par Prof. Lavoie après 3 jours, entente, décision du conseil.
- **Étapes** : 1. envoyer la demande ; 2. avancer de 3 jours ; 3. proposer l'entente ; 4. la soumettre au conseil ; 5. tenter de soumettre une entente sans demande acceptée ; 6. le conseil approuve.
- **Résultat attendu** : états successifs ENVOYEE, ACCEPTEE, puis entente PROPOSEE, SOUMISE_CONSEIL, APPROUVEE. L'étape 5 est refusée. À l'approbation, le projet apparaît dans le plan avec ses 3 crédits.

### T22 · Projet non admissible et refus sans motif · EX-12 · E
- **Objectif** : vérifier l'admissibilité et l'obligation d'un motif.
- **Préconditions** : D1 (30 crédits acquis).
- **Entrées** : demande sur P3 (60 crédits requis) ; refus du conseil sur une entente sans motif.
- **Étapes** : 1. demander P3 ; 2. sur une entente soumise, tenter un refus sans motif ; 3. refuser avec un motif.
- **Résultat attendu** : étape 1 BLOQUANTE « 60 crédits requis, 30 acquis », aucune demande créée. Étape 2 rejetée. Étape 3 : entente REFUSEE avec le motif affiché à la personne étudiante.

### T23 · Intention en vue multi-sessions · EX-13 · L
- **Objectif** : vérifier l'offre estimée et l'ordre des préalables.
- **Préconditions** : plan A26 contenant IFT2015 ; aucun horaire publié pour H27.
- **Entrées** : intention de IFT3395 en H27 ; intention de IFT3395 dans une H27 où IFT2015 est aussi planifié en H27.
- **Étapes** : 1. ajouter l'intention de IFT3395 en H27 ; 2. consulter le plan ; 3. déplacer IFT2015 en H27 et revérifier.
- **Résultat attendu** : étapes 1 et 2, élément en état INTENTION marqué « offre estimée », absent du total de crédits confirmés, IFT2015 (planifié avant) envoyé à Planifium comme réussi et le verdict ne bloque pas. Étape 3, verdict BLOQUANTE parce que le préalable est planifié dans la même session.

### T24 · Planifium indisponible · EX-17, EX-03, EX-04 · E
- **Objectif** : vérifier le repli sur la copie datée et le statut NON_VERIFIABLE (R9, R11).
- **Préconditions** : copie en cache de IFT3395 datée de 30 heures, Planifium retourne une erreur de délai. Deuxième scénario : cache vide.
- **Entrées** : ajout de IFT2105 au plan, avec le plan au plafond moins 3 crédits.
- **Étapes** : 1. ajouter le cours avec le cache de 30 heures ; 2. vider le cache et refaire l'ajout ; 3. ajouter ensuite un cours qui ferait dépasser le plafond.
- **Résultat attendu** : étape 1, la copie est utilisée et affichée « données du … », les règles déléguées (préalables, conflits) sont NON_VERIFIABLE (non bloquantes, jamais RESPECTEE). Étape 2, catalogue indisponible signalé, l'ajout est enregistré avec la mention « non vérifiable ». Étape 3, ReglePlafondCredits donne quand même BLOQUANTE puisqu'elle ne dépend pas de Planifium.

### T25 · Repères partagés et modération · EX-15 · N
- **Objectif** : vérifier la modération, l'anonymat et l'expiration.
- **Préconditions** : une personne étudiante soumet un repère sur IFT2255 en A26 (« charge réelle d'environ 12 h par semaine »), un conseil de programme modérateur.
- **Entrées** : soumission, publication, deuxième repère refusé, consultation à plusieurs dates.
- **Étapes** : 1. soumettre ; 2. consulter l'offre avant modération ; 3. le conseil publie ; 4. consulter ; 5. soumettre un second repère que le conseil refuse ; 6. consulter après la fin de la deuxième session suivant la soumission.
- **Résultat attendu** : étape 2, le repère est EN_MODERATION et invisible. Étape 4, statut PUBLIE, texte affiché sans nom d'auteur. Étape 5, le repère refusé n'est jamais affiché. Étape 6, le repère n'est plus affiché.

## 5.4 Couverture

| Exigence | Tests | N | L | E |
| --- | --- | --- | --- | --- |
| EX-01 | T01 | 1 | | |
| EX-02 | T02, T03 | 1 | | 1 |
| EX-03 | T04, T05, T24 | 1 | 1 | 1 |
| EX-04 | T06, T24 | | | 2 |
| EX-05 | T07 | 1 | | |
| EX-06 | T08 | 1 | | |
| EX-07 | T09, T10 | | | 2 |
| EX-08 | T11 | | 1 | |
| EX-09 | T14, T15 | | 2 | |
| EX-10 | T16, T17, T18, T19 | 3 | | 1 |
| EX-11 | T20 | 1 | | |
| EX-12 | T21, T22 | 1 | | 1 |
| EX-13 | T23 | | 1 | |
| EX-14 | T12 | 1 | | |
| EX-15 | T25 | 1 | | |
| EX-16 | T13 | | 1 | |
| EX-17 | T09, T24 | | | 2 |

Les 17 exigences sont couvertes. Les cas se répartissent en 12 nominaux, 6 limites (T05, T11, T13, T14, T15, T23) et 7 échecs (T03, T06, T09, T10, T17, T22, T24).

## Colonne « Tests (B3) » de la matrice de traçabilité (§7)

| Exigence | Tests |
| --- | --- |
| EX-01 | T01 |
| EX-02 | T02, T03 |
| EX-03 | T04, T05, T24 |
| EX-04 | T06, T24 |
| EX-05 | T07 |
| EX-06 | T08 |
| EX-07 | T09, T10 |
| EX-08 | T11 |
| EX-09 | T14, T15 |
| EX-10 | T16, T17, T18, T19 |
| EX-11 | T20 |
| EX-12 | T21, T22 |
| EX-13 | T23 |
| EX-14 | T12 |
| EX-15 | T25 |
| EX-16 | T13 |
| EX-17 | T09, T24 |
