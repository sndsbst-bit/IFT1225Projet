# Usage : python3 generer_classes.py .   (depuis docs/diagrammes/phase2/), puis java -jar plantuml.jar -tpng B2-*.puml
# Génère les diagrammes de classes B2 à partir d'une seule définition (cohérence garantie
# entre la vue principale et les annexes).
import sys, os

OUT = sys.argv[1]

P = "persistant BD"      # conservé d'une visite à l'autre, serveur (PostgreSQL)
C = "copie datée BD"     # copie datée d'une réponse Planifium, serveur (PostgreSQL)

# nom -> (composant, déclaration, stéréotype, corps)
K = {}
def cls(name, comp, body, kind="class", st=None):
    K[name] = (comp, kind, st, body.strip("\n"))

# ---------------- Service de profil ----------------
cls("ProfilEtudiant", "Service de profil", """
- id : UUID
- matricule : String
- programmeId : String
- parcours : String [0..1]
- coursReussis : Set<String>
- creditsAcquis : double
- moyenne : Double [0..1]
- provenance : Provenance
- importeLe : LocalDateTime [0..1]
--
+ estVerifie() : boolean
+ aReussi(sigle : String) : boolean
""", st=P)
cls("ProfilService", "Service de profil", """
+ lireProfil(etudiantId : UUID) : ProfilEtudiant
+ importerDossier(etudiantId : UUID, consentement : boolean) : ProfilEtudiant
+ saisirManuellement(etudiantId : UUID, coursReussis : Set<String>) : ProfilEtudiant
""", st="service")
cls("Provenance", "Service de profil", "IMPORTEE_SYNCHRO\nSAISIE_MANUELLE", kind="enum")

# ---------------- Catalogue de l'offre ----------------
cls("Programme", "Catalogue de l'offre", """
- id : String
- nom : String
- recupereLe : LocalDateTime
--
+ blocsContenant(sigle : String) : List<Bloc>
+ compteDansProgramme(sigle : String) : boolean
""", st=C)
cls("Segment", "Catalogue de l'offre", """
- id : String
- nom : String
""", st=C)
cls("Parcours", "Catalogue de l'offre", """
- titre : String
- type : String
--
+ inclut(segmentId : String) : boolean
""", st=C)
cls("Bloc", "Catalogue de l'offre", """
- id : String
- type : TypeBloc
- creditsMin : int
- creditsMax : int
- sigles : List<String>
--
+ accepte(sigle : String) : boolean
+ creditsComptes(reussis : List<Cours>) : double
+ estSatisfait(reussis : List<Cours>) : boolean
""", st=C)
cls("TypeBloc", "Catalogue de l'offre", "OBLIGATOIRE\nOPTION\nCHOIX\n--\n+ {static} depuis(texte : String) : TypeBloc", kind="enum")
cls("Cours", "Catalogue de l'offre", """
- sigle : String
- titre : String
- credits : double
- saisonsHabituelles : Set<Saison>
- statutAnalyse : StatutAnalyse
- recupereLe : LocalDateTime
--
+ sectionsPour(session : String) : List<Section>
+ estHabituellementOffertA(saison : Saison) : boolean
""", st=C)
cls("Section", "Catalogue de l'offre", """
- id : String
- session : String
- capacite : Integer [0..1]
- inscrits : Integer [0..1]
- synthetique : boolean
- misAJourLe : LocalDate
--
+ placesRestantes() : Integer [0..1]
+ chevauche(autre : Section) : boolean
""", st=C)
cls("Rencontre", "Catalogue de l'offre", """
- type : String
- jour : DayOfWeek
- debut : LocalTime
- fin : LocalTime
- mode : String
- dateDebut : LocalDate
- dateFin : LocalDate
--
+ chevauche(autre : Rencontre) : boolean
""", st=C)
cls("Exigence", "Catalogue de l'offre", """
+ {abstract} siglesMentionnes() : Set<String>
+ {abstract} textesAVerifier() : List<String>
""", kind="abstract class", st=C)
cls("ExigenceCours", "Catalogue de l'offre", "- sigle : String", st=C)
cls("ExigenceCombinee", "Catalogue de l'offre", "", kind="abstract class", st=C)
cls("ExigenceToutes", "Catalogue de l'offre", "", st=C)
cls("ExigenceUneParmi", "Catalogue de l'offre", "", st=C)
cls("ExigenceAuMoins", "Catalogue de l'offre", "- nombre : int", st=C)
cls("ExigenceCredits", "Catalogue de l'offre", "- min : int\n- max : Integer [0..1]\n- portee : String", st=C)
cls("ExigenceManuelle", "Catalogue de l'offre", "- texte : String", st=C)
cls("StatutAnalyse", "Catalogue de l'offre", "EXACT\nPARTIEL\nMANUEL\nAUCUNE", kind="enum")
cls("Saison", "Catalogue de l'offre", "AUTOMNE\nHIVER\nETE", kind="enum")
cls("OffreEncadree", "Catalogue de l'offre", """
- id : UUID
- type : TypeOffre
- titre : String
- domaine : String
- credits : double
- capacite : int
- creditsMinimum : int
- delaiReponseJours : int
- etat : EtatOffre
- responsableId : UUID
--
+ placesRestantes() : int
+ estAdmissible(profil : ProfilEtudiant) : boolean
+ peutEtreModifieePar(personneId : UUID) : boolean
""", st=P)
cls("TypeOffre", "Catalogue de l'offre", "PROJET_SUPERVISE\nPOSTE_LABO\nSTAGE\nSEMINAIRE\nCONCOURS\nACTIVITE", kind="enum")
cls("EtatOffre", "Catalogue de l'offre", "BROUILLON\nEN_VALIDATION\nPUBLIEE\nRETIREE", kind="enum")
cls("Repere", "Catalogue de l'offre", """
- id : UUID
- cible : String
- texte : String
- statut : StatutRepere
- auteurId : UUID
- soumisLe : LocalDate
- expireLe : LocalDate
--
+ estVisible(aujourdhui : LocalDate) : boolean
""", st=P)
cls("StatutRepere", "Catalogue de l'offre", "EN_MODERATION\nPUBLIE\nREFUSE", kind="enum")
cls("FiltreOffre", "Catalogue de l'offre", """
- texte : String [0..1]
- types : Set<TypeOffre>
- domaine : String [0..1]
- session : String
- admissiblesSeulement : boolean
""")
cls("CatalogueService", "Catalogue de l'offre", """
+ rechercher(filtre : FiltreOffre, profil : ProfilEtudiant) : ResultatRecherche
+ cours(sigle : String, session : String) : Cours
+ programme(id : String) : Programme
+ publierOffre(auteurId : UUID, offre : OffreEncadree) : OffreEncadree
+ modifierOffre(auteurId : UUID, offre : OffreEncadree) : OffreEncadree
+ validerOffre(offreId : UUID, approuvee : boolean) : OffreEncadree
+ retirerOffre(auteurId : UUID, offreId : UUID) : void
+ soumettreRepere(etudiantId : UUID, cible : String, texte : String) : Repere
+ modererRepere(repereId : UUID, accepte : boolean) : Repere
""", st="service")
cls("ResultatRecherche", "Catalogue de l'offre", """
- cours : List<Cours>
- offres : List<OffreEncadree>
- filtresLesPlusRestrictifs : List<String>
- donneesDatees : LocalDateTime
""")

# ---------------- Service de planification ----------------
cls("PlanDeSession", "Service de planification", """
- id : UUID
- session : String
- statut : StatutPlan
- consequenceTempsPartielAcceptee : boolean
--
+ ajouter(element : ElementPlan) : void
+ retirer(elementId : UUID) : void
+ totalCredits() : double
+ sectionsChoisies() : List<String>
""", st=P)
cls("ElementPlan", "Service de planification", """
- id : UUID
- etat : EtatElement
- credits : double
- ajouteLe : LocalDateTime
--
+ estCredite() : boolean
""", st=P)
cls("EtatElement", "Service de planification", "PREVU\nDEMANDE\nCONFIRME\nINTENTION", kind="enum")
cls("StatutPlan", "Service de planification", "BROUILLON\nCONFIRME", kind="enum")
cls("PlanificationService", "Service de planification", """
+ ajouterCours(planId : UUID, sigle : String, sectionId : String) : List<Verdict>
+ ajouterOffre(planId : UUID, offreId : UUID) : List<Verdict>
+ retirerElement(planId : UUID, elementId : UUID) : List<Verdict>
+ confirmerPlan(planId : UUID, consequenceAcceptee : boolean) : List<Verdict>
+ projeterIntention(etudiantId : UUID, session : String, sigle : String) : List<Verdict>
+ calculerProgression(etudiantId : UUID) : Map<String, Double>
""", st="service")

# ---------------- Service des demandes ----------------
cls("Demande", "Service des demandes", """
- id : UUID
- etat : EtatDemande
- message : String
- envoyeeLe : LocalDate
- echeanceReponse : LocalDate
- relanceUtilisee : boolean
- motifRefus : String [0..1]
--
+ relancer(aujourdhui : LocalDate, prolongationJours : int) : void
+ expirer(aujourdhui : LocalDate) : boolean
+ joursRestants(aujourdhui : LocalDate) : long
""", st=P)
cls("EtatDemande", "Service des demandes", "ENVOYEE\nRELANCEE\nACCEPTEE\nREFUSEE\nRETIREE\nEXPIREE", kind="enum")
cls("Entente", "Service des demandes", """
- id : UUID
- sujet : String
- credits : double
- etat : EtatEntente
- motifRefus : String [0..1]
--
+ approuver(approuve : boolean, motif : String) : void
""", st=P)
cls("EtatEntente", "Service des demandes", "PROPOSEE\nSOUMISE_CONSEIL\nAPPROUVEE\nREFUSEE", kind="enum")
cls("IndicateurDisponibilite", "Service des demandes", """
- placesRestantes : int
- demandesEnAttente : int
- delaiHabituelJours : Integer [0..1]
- demandesTraiteesBase : int
- calculeLe : LocalDateTime
""")
cls("DemandeService", "Service des demandes", """
+ envoyer(etudiantId : UUID, offreId : UUID, message : String) : Demande
+ relancer(demandeId : UUID) : Demande
+ rediriger(demandeId : UUID, nouvelleOffreId : UUID) : Demande
+ repondre(demandeId : UUID, accepte : boolean, motif : String) : Demande
+ proposerEntente(demandeId : UUID, sujet : String, credits : double) : Entente
+ deciderEntente(ententeId : UUID, approuve : boolean, motif : String) : Entente
+ traiterDelais(aujourdhui : LocalDate) : int
+ fermerDemandesDe(offreId : UUID) : int
+ indicateur(offreId : UUID) : IndicateurDisponibilite
""", st="service")

# ---------------- Moteur de règles ----------------
cls("MoteurRegles", "Moteur de règles", """
- regles : List<Regle>
--
+ verifier(plan : PlanDeSession, profil : ProfilEtudiant, programme : Programme) : List<Verdict>
+ {static} estBloquant(verdicts : List<Verdict>) : boolean
""", st="service")
cls("Regle", "Moteur de règles", """
+ code() : String
+ evaluer(plan : PlanDeSession, profil : ProfilEtudiant, programme : Programme) : List<Verdict>
""", kind="interface")
cls("Verdict", "Moteur de règles", """
- codeRegle : String
- statut : StatutVerdict
- message : String
- aVerifier : List<String>
- elementId : UUID [0..1]
--
+ estBloquant() : boolean
""")
cls("StatutVerdict", "Moteur de règles", "RESPECTEE\nAVERTISSEMENT\nBLOQUANTE\nA_VERIFIER\nNON_VERIFIABLE", kind="enum")
cls("RegleEligibilite", "Moteur de règles", "- source : SourceCatalogue\n' EX-03, EX-13 (déléguée à Planifium)")
cls("RegleConflitHoraire", "Moteur de règles", "- source : SourceCatalogue\n' EX-04 (déléguée à Planifium)")
cls("ReglePlafondCredits", "Moteur de règles", "- plafond : int = 18\n' EX-16")
cls("RegleTempsPlein", "Moteur de règles", "- seuil : int = 12\n- consequence : String\n' EX-08")
cls("RegleRattachementProgramme", "Moteur de règles", "' EX-05 : utilise Programme.blocsContenant()")
cls("RegleCapaciteOffre", "Moteur de règles", "' EX-07 : OffreEncadree.placesRestantes()")
cls("RegleEcheance", "Moteur de règles", "- echeances : EcheanceRepository\n- horloge : Clock\n' EX-09")

# ---------------- Adaptateurs et cache ----------------
cls("SourceCatalogue", "Adaptateur Planifium", """
+ chercherCours(sigles : List<String>, session : String) : List<Cours>
+ lireProgramme(id : String) : Programme
+ verifierPlan(session : String, sections : List<String>, reussis : Set<String>, programmeId : String) : List<Verdict>
""", kind="interface")
cls("PlanifiumAdapter", "Adaptateur Planifium", """
- urlBase : String
- delaiMaxMs : int
- cache : CacheSources
--
+ chercherCours(sigles : List<String>, session : String) : List<Cours>
+ lireProgramme(id : String) : Programme
+ verifierPlan(session : String, sections : List<String>, reussis : Set<String>, programmeId : String) : List<Verdict>
- versVerdict(statut : String, aVerifier : List<String>) : Verdict
- verifierSiglesInconnus(demandes : List<String>, recus : List<String>) : List<String>
""", st="adaptateur")
cls("CacheSources", "Cache des sources", """
+ enregistrer(cle : String, source : String, json : String) : void
+ relire(cle : String) : Optional<ReponseEnCache>
""", st="service")
cls("ReponseEnCache", "Cache des sources", """
- cle : String
- source : String
- contenuJson : String
- recupereeLe : LocalDateTime
- miseAJourSource : LocalDate [0..1]
--
+ age() : Duration
""", st=C)
cls("SourceDossier", "Adaptateur Synchro", "+ lireDossier(matricule : String) : ProfilEtudiant", kind="interface")
cls("SynchroAdapter", "Adaptateur Synchro", "- urlBase : String\n--\n+ lireDossier(matricule : String) : ProfilEtudiant", st="adaptateur")
cls("CalendrierAdapter", "Adaptateur Calendrier", "- urlIcal : String\n--\n+ lireEcheances(session : String) : List<Echeance>", st="adaptateur")

# ---------------- Échéances, notification, dépôts, contrôleurs ----------------
cls("Echeance", "Gestionnaire des échéances", """
- id : UUID
- type : TypeEcheance
- session : String
- date : LocalDate
- consequence : String
--
+ estDepassee(aujourdhui : LocalDate) : boolean
+ joursAvant(aujourdhui : LocalDate) : long
""", st=P)
cls("TypeEcheance", "Gestionnaire des échéances", "MODIFICATION_SANS_FRAIS\nABANDON_AVEC_FRAIS\nFIN_TRIMESTRE", kind="enum")
cls("GestionnaireEcheances", "Gestionnaire des échéances", """
- horloge : Clock
--
+ executerQuotidien() : void
+ importerCalendrier() : void
+ rafraichirOffre(session : String) : void
""", st="service")
cls("Notificateur", "Notificateur", "+ envoyer(destinataire : String, sujet : String, corps : String) : void", st="service")
cls("PlanRepository", "Dépôts", "+ findByEtudiantIdAndSession(id : UUID, session : String) : Optional<PlanDeSession>", kind="interface")
cls("DemandeRepository", "Dépôts", "+ findByEtatAndEcheanceReponseBefore(etat : EtatDemande, d : LocalDate) : List<Demande>", kind="interface")
cls("EcheanceRepository", "Dépôts", "+ findBySession(session : String) : List<Echeance>", kind="interface")
cls("ControleurPlan", "Contrôleurs REST", """
+ ajouter(planId : UUID, sigle : String, sectionId : String) : ResponseEntity<List<Verdict>>
+ confirmer(planId : UUID, consequenceAcceptee : boolean) : ResponseEntity<List<Verdict>>
""", st="RestController")
cls("ControleurDemandes", "Contrôleurs REST", """
+ envoyer(offreId : UUID, message : String) : ResponseEntity<Demande>
+ relancer(demandeId : UUID) : ResponseEntity<Demande>
""", st="RestController")

HEADER = """@startuml {name}
skinparam defaultFontName DejaVu Sans
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam packageStyle rectangle
skinparam linetype polyline
skinparam nodesep 40
skinparam ranksep 50
skinparam class {{
  BackgroundColor #FFFFFF
  BorderColor #2F4F6F
  BackgroundColor<<persistant BD>> #DDEFD9
  BackgroundColor<<copie datée BD>> #FFF1C9
  BackgroundColor<<service>> #E3ECF7
  BackgroundColor<<adaptateur>> #F3E1F2
}}
hide empty members
title {title}
"""

LEGEND = """
legend right
  <back:#DDEFD9> «persistant BD» </back> conservé d'une visite à l'autre, serveur (PostgreSQL)
  <back:#FFF1C9> «copie datée BD» </back> copie datée d'une réponse Planifium, serveur (PostgreSQL)
  <back:#E3ECF7> «service» </back> / <back:#F3E1F2> «adaptateur» </back> : non conservés (logique)
  Sans couleur : objets de calcul ou de présentation, non conservés
  Chaque cadre porte le nom du composant B1 qui héberge ses classes.
endlegend
"""

def render(name, title, names, rels, notes=""):
    lines = [HEADER.format(name=name, title=title)]
    comps = []
    for n in names:
        c = K[n][0]
        if c not in comps: comps.append(c)
    for c in comps:
        lines.append(f'package "{c}" {{')
        for n in names:
            comp, kind, st, body = K[n]
            if comp != c: continue
            stt = f" <<{st}>>" if st else ""
            lines.append(f"  {kind} {n}{stt} {{")
            for b in body.splitlines():
                if b.startswith("'"):
                    lines.append("    .. " + b[1:].strip() + " ..")
                else:
                    lines.append("    " + b)
            lines.append("  }")
        lines.append("}")
    lines.append(rels.strip("\n"))
    lines.append(notes)
    lines.append(LEGEND)
    lines.append("@enduml")
    with open(os.path.join(OUT, name + ".puml"), "w") as f:
        f.write("\n".join(lines) + "\n")

# ================= Vue principale (15 classes) =================
MAIN = ["ProfilEtudiant",
        "Programme", "Bloc", "Cours", "Section", "Exigence", "OffreEncadree",
        "PlanDeSession", "ElementPlan", "PlanificationService",
        "Demande",
        "MoteurRegles", "Regle", "Verdict",
        "PlanifiumAdapter"]
assert len(MAIN) == 15
MAIN_RELS = """
ProfilEtudiant "1" -- "0..*" PlanDeSession : planifie >
ProfilEtudiant "0..*" --> "1" Programme : inscrit à >
ProfilEtudiant "1" -- "0..*" Demande : envoie >
Programme "1" *-- "1..*" Bloc : structure (par segments)
Bloc "0..*" o-- "0..*" Cours : liste >
Cours "1" *-- "0..*" Section : offerte en >
Cours "1" *-- "0..1" Exigence : préalables >
PlanDeSession "1" *-- "0..*" ElementPlan : contient >
ElementPlan "0..*" --> "0..1" Cours : {xor}
ElementPlan "0..*" --> "0..1" Section : section choisie >
ElementPlan "0..*" --> "0..1" OffreEncadree : {xor}
Demande "0..*" --> "1" OffreEncadree : vise >
Demande "0..1" -- "0..1" ElementPlan : réserve >
PlanificationService --> MoteurRegles : fait vérifier >
PlanificationService ..> PlanDeSession : modifie >
MoteurRegles "1" o-- "1..*" Regle : applique >
Regle ..> Verdict : produit >
Regle ..> PlanifiumAdapter : délègue préalables\\net conflits >
PlanifiumAdapter ..> Cours : crée (mapping) >
PlanifiumAdapter ..> Programme : crée (mapping) >
PlanifiumAdapter ..> Verdict : traduit yes/no/unknown >
"""
MAIN_NOTES = """
note as NRegles
  <b>Où vivent les règles du programme</b>
  Plafond de crédits : ReglePlafondCredits (plafond = 18)
  Temps plein : RegleTempsPlein (seuil = 12)
  Préalables : arbre Exigence (donnée) + RegleEligibilite,
  qui délègue l'évaluation à Planifium (logique)
  Blocs : Bloc.accepte(), Bloc.creditsComptes() (donnée)
  + RegleRattachementProgramme (logique)
  Détail des 7 règles : annexe 4
end note
NRegles .. Regle
note bottom of Exigence
  Composite : ExigenceCours, ExigenceToutes,
  ExigenceUneParmi, ExigenceAuMoins,
  ExigenceCredits, ExigenceManuelle (annexe 3)
end note
"""
render("B2-classes-vue-principale", "B2 — Diagramme de classes : vue principale (15 classes)", MAIN, MAIN_RELS, MAIN_NOTES)

# ================= Annexe B2-a : modèle =================
A = ["ProfilEtudiant", "Provenance",
     "Programme", "Segment", "Parcours", "Bloc", "TypeBloc", "Cours", "StatutAnalyse", "Saison", "Section", "Rencontre",
     "Exigence", "ExigenceCours", "ExigenceCombinee", "ExigenceToutes", "ExigenceUneParmi", "ExigenceAuMoins",
     "ExigenceCredits", "ExigenceManuelle", "OffreEncadree", "TypeOffre", "EtatOffre", "Repere", "StatutRepere",
     "PlanDeSession", "StatutPlan", "ElementPlan", "EtatElement",
     "Demande", "EtatDemande", "Entente", "EtatEntente",
     "Echeance", "TypeEcheance", "ReponseEnCache"]
A_RELS = """
ProfilEtudiant "1" -- "0..*" PlanDeSession : planifie >
ProfilEtudiant "0..*" --> "1" Programme : inscrit à >
ProfilEtudiant "1" -- "0..*" Demande : envoie >
ProfilEtudiant --> Provenance
Programme "1" *-- "1..*" Segment
Programme "1" *-- "0..*" Parcours
Parcours "0..*" --> "1..*" Segment : regroupe >
Segment "1" *-- "1..*" Bloc
Bloc --> TypeBloc
Bloc "0..*" o-- "0..*" Cours : liste >
Cours "1" *-- "0..*" Section : offerte en >
Cours "1" *-- "0..1" Exigence : préalables >
Cours --> StatutAnalyse
Cours --> Saison
Section "1" *-- "0..*" Rencontre
Exigence <|-- ExigenceCours
Exigence <|-- ExigenceCombinee
Exigence <|-- ExigenceCredits
Exigence <|-- ExigenceManuelle
ExigenceCombinee "1" *-- "1..*" Exigence : items >
ExigenceCombinee <|-- ExigenceToutes
ExigenceCombinee <|-- ExigenceUneParmi
ExigenceCombinee <|-- ExigenceAuMoins
OffreEncadree --> TypeOffre
OffreEncadree --> EtatOffre
ProfilEtudiant "1" -- "0..*" Repere : propose (auteur jamais affiché) >
Repere --> StatutRepere
PlanDeSession "1" *-- "0..*" ElementPlan : contient >
PlanDeSession --> StatutPlan
ElementPlan --> EtatElement
ElementPlan "0..*" --> "0..1" Cours : {xor}
ElementPlan "0..*" --> "0..1" Section : section choisie >
ElementPlan "0..*" --> "0..1" OffreEncadree : {xor}
Demande "0..*" --> "1" OffreEncadree : vise >
Demande "0..1" -- "0..1" ElementPlan : réserve >
Demande --> EtatDemande
Demande "1" *-- "0..1" Entente : aboutit à >
Entente --> EtatEntente
Echeance --> TypeEcheance
"""
A_NOTES = """
note bottom of EtatDemande
  RETIREE et EXPIREE sont des états internes
  de Boussole (délai dépassé, redirection),
  pas des décisions officielles.
end note
note bottom of Repere
  Visible seulement si PUBLIE et avant expireLe
  (fin de la 2e session après sa soumission).
end note
"""
render("B2-classes-annexe-a-modele", "B2 — Annexe 3 : modèle complet (catalogue, plan, demandes, échéances, cache)", A, A_RELS, A_NOTES)

# ================= Annexe B2-b : services, règles, adaptateurs =================
B = ["ControleurPlan", "ControleurDemandes",
     "PlanificationService", "DemandeService", "IndicateurDisponibilite",
     "CatalogueService", "FiltreOffre", "ResultatRecherche", "ProfilService",
     "MoteurRegles", "Regle", "Verdict", "StatutVerdict",
     "RegleEligibilite", "RegleConflitHoraire", "ReglePlafondCredits", "RegleTempsPlein",
     "RegleRattachementProgramme", "RegleCapaciteOffre", "RegleEcheance",
     "SourceCatalogue", "PlanifiumAdapter", "CacheSources", "SourceDossier", "SynchroAdapter",
     "CalendrierAdapter", "GestionnaireEcheances", "Notificateur",
     "PlanRepository", "DemandeRepository", "EcheanceRepository"]
B_RELS = """
ControleurPlan --> PlanificationService
ControleurDemandes --> DemandeService
PlanificationService --> MoteurRegles : fait vérifier >
PlanificationService --> CatalogueService
PlanificationService --> ProfilService
PlanificationService --> PlanRepository
DemandeService --> MoteurRegles : admissibilité >
DemandeService --> DemandeRepository
DemandeService --> Notificateur
DemandeService ..> IndicateurDisponibilite : calcule >
CatalogueService --> SourceCatalogue
CatalogueService --> DemandeService : ferme les demandes d'une offre retirée >
CatalogueService ..> FiltreOffre
CatalogueService ..> ResultatRecherche : produit >
ProfilService --> SourceDossier
MoteurRegles "1" o-- "1..*" Regle : applique >
Regle ..> Verdict : produit >
Verdict --> StatutVerdict
Regle <|.. RegleEligibilite
Regle <|.. RegleConflitHoraire
Regle <|.. ReglePlafondCredits
Regle <|.. RegleTempsPlein
Regle <|.. RegleRattachementProgramme
Regle <|.. RegleCapaciteOffre
Regle <|.. RegleEcheance
RegleEligibilite --> SourceCatalogue
RegleConflitHoraire --> SourceCatalogue
RegleEcheance --> EcheanceRepository
SourceCatalogue <|.. PlanifiumAdapter
PlanifiumAdapter --> CacheSources : copie datée >
SourceDossier <|.. SynchroAdapter
GestionnaireEcheances --> DemandeService : délais échus >
GestionnaireEcheances --> CalendrierAdapter
GestionnaireEcheances --> SourceCatalogue : rafraîchit >
GestionnaireEcheances --> Notificateur
GestionnaireEcheances --> EcheanceRepository
"""
render("B2-classes-annexe-b-services", "B2 — Annexe 4 : services, règles, adaptateurs, dépôts", B, B_RELS)

# Vérification : chaque classe est rattachée à un composant B1, et chaque composant a au moins une classe.
B1 = ["Contrôleurs REST", "Service de planification", "Service des demandes", "Catalogue de l'offre",
      "Service de profil", "Moteur de règles", "Gestionnaire des échéances", "Adaptateur Planifium",
      "Cache des sources", "Adaptateur Synchro", "Adaptateur Calendrier", "Notificateur", "Dépôts"]
used = {v[0] for v in K.values()}
assert used <= set(B1), used - set(B1)
missing = [c for c in B1 if c not in used]
assert not missing, missing
allshown = set(MAIN) | set(A) | set(B)
assert allshown == set(K), set(K) - allshown
print("OK", len(K), "classes ; composants couverts :", len(B1))
