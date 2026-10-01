// API simulée : remplace l'« API applicative » et la base de données du C4 (niveau 2).
// Elle charge les données JSON (qui remplacent le « Service d'import ») et garde l'état en mémoire.
// Toute la logique métier est déléguée à regles.js et demandes.js.

import * as R from "./regles.js";
import * as D from "./demandes.js";

export async function chargerDonnees() {
  const lire = async (f) => {
    const rep = await fetch(`data/${f}`);
    if (!rep.ok) throw new Error(`Impossible de charger data/${f}`);
    return rep.json();
  };
  const [offre, dossier, regles] = await Promise.all([lire("offre.json"), lire("dossier.json"), lire("regles.json")]);
  return { offre, dossier, regles };
}

export function creerEtat({ offre, dossier, regles }) {
  return {
    offre: structuredClone(offre),
    dossier,
    regles,
    date: regles.dateDebut,
    plan: { cours: [], projets: [], activites: [], confirme: false },
    demandes: [],
    journal: [],
  };
}

function journaliser(etat, texte, type = "info") {
  etat.journal.unshift({ date: etat.date, texte, type });
}

// ---- Plan de session (CU03) ----

export function ajouterCours(etat, code) {
  const verif = R.verifierAjoutCours(code, etat);
  if (verif.ok) {
    etat.plan.cours.push(code);
    etat.plan.confirme = false;
    journaliser(etat, `${code} ajouté au plan.`, "succes");
  } else {
    journaliser(etat, `Ajout de ${code} refusé : ${verif.bloquantes[0].message}`, "erreur");
  }
  return verif;
}

export function retirerCours(etat, code) {
  etat.plan.cours = etat.plan.cours.filter((c) => c !== code);
  etat.plan.confirme = false;
  journaliser(etat, `${code} retiré du plan.`);
}

export function ajouterActivite(etat, id) {
  const a = etat.offre.activites.find((x) => x.id === id);
  if (a.inscrits >= a.places) return { ok: false, message: `« ${a.titre} » est complet.` };
  if (!etat.plan.activites.includes(id)) etat.plan.activites.push(id);
  journaliser(etat, `Activité « ${a.titre} » ajoutée (0 crédit, ne compte pas dans le programme).`);
  return { ok: true };
}

export function retirerActivite(etat, id) {
  etat.plan.activites = etat.plan.activites.filter((x) => x !== id);
}

/** EX-08 : la confirmation exige d'avoir vu la conséquence du temps partiel. */
export function confirmerPlan(etat, { accepteTempsPartiel = false } = {}) {
  const tp = R.etatTempsPlein(etat.plan, etat.offre, etat.regles);
  if (tp.sousSeuil && !accepteTempsPartiel) {
    return { ok: false, avertissement: tp };
  }
  etat.plan.confirme = true;
  journaliser(etat, `Plan confirmé (${tp.credits} crédits${tp.sousSeuil ? ", temps partiel accepté" : ""}). Inscrivez-vous maintenant dans Synchro.`, "succes");
  return { ok: true };
}

// ---- Demandes de projet (CU05, CU06) ----

export function envoyerDemande(etat, projetId) {
  const projet = etat.offre.projets.find((p) => p.id === projetId);
  const adm = R.admissibiliteProjet(projet, etat);
  if (!adm.ok) {
    journaliser(etat, `Demande pour « ${projet.titre} » impossible : ${adm.message}`, "erreur");
    return adm;
  }
  const d = D.creerDemande(projet, etat.date, etat.regles);
  etat.demandes.push(d);
  journaliser(etat, `Demande envoyée à ${projet.encadrant}. Réponse attendue au plus tard le ${d.echeance}.`);
  return { ok: true, demande: d };
}

function remplacer(etat, nouvelle) {
  etat.demandes = etat.demandes.map((d) => (d.id === nouvelle.id ? nouvelle : d));
}

export function relancerDemande(etat, id) {
  const d = D.relancer(etat.demandes.find((x) => x.id === id), etat.regles);
  remplacer(etat, d);
  journaliser(etat, `Relance envoyée. Nouveau délai : ${d.echeance}.`);
}

/** Retire la demande et renvoie les projets équivalents encore accessibles. */
export function redirigerDemande(etat, id) {
  const ancienne = etat.demandes.find((x) => x.id === id);
  remplacer(etat, D.retirer(ancienne));
  const suggestions = etat.offre.projets.filter(
    (p) => p.id !== ancienne.projetId && R.admissibiliteProjet(p, etat).ok
  );
  journaliser(etat, `Demande retirée. Offres équivalentes : ${suggestions.map((p) => p.titre).join(", ") || "aucune"}.`);
  return suggestions;
}

export function accepterOffre(etat, id) {
  const d = D.accepterOffre(etat.demandes.find((x) => x.id === id));
  remplacer(etat, d);
  const projet = etat.offre.projets.find((p) => p.id === d.projetId);
  projet.inscrits += 1;
  etat.plan.projets.push(projet.id);
  etat.plan.confirme = false;
  journaliser(etat, `Projet « ${projet.titre} » confirmé (+${projet.credits} crédits). Approbation du conseil de programme simulée.`, "succes");
}

// ---- Temps (Ordonnanceur) ----

export function avancerUnJour(etat) {
  etat.date = D.ajouterJours(etat.date, 1);
  if (etat.date === D.ajouterJours(etat.regles.dateLimiteModification, 1)) {
    journaliser(etat, `La date limite de modification (${etat.regles.dateLimiteModification}) est passée.`, "erreur");
  }
  etat.demandes = etat.demandes.map((d) => {
    const projet = etat.offre.projets.find((p) => p.id === d.projetId);
    const { demande, evenement } = D.avancerDemande(d, projet, etat.date, etat.regles);
    if (evenement) journaliser(etat, evenement, demande.etat === "expiree" || demande.etat === "refusee" ? "erreur" : "rappel");
    return demande;
  });
}
