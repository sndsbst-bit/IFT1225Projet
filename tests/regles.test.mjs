// Tests du moteur de règles et du cycle des demandes. Lancer : node --test tests/*.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as R from "../prototype/js/regles.js";
import * as D from "../prototype/js/demandes.js";

const lire = (f) => JSON.parse(readFileSync(new URL(`../prototype/data/${f}`, import.meta.url)));
const offre = lire("offre.json");
const dossier = lire("dossier.json");
const regles = lire("regles.json");
const ctx = (plan = { cours: [], projets: [], activites: [] }, date = regles.dateDebut) => ({ plan, offre, dossier, regles, date });

test("EX-03 : un préalable manquant bloque l'ajout et est nommé", () => {
  const v = R.verifierAjoutCours("IFT3395", ctx());
  assert.equal(v.ok, false);
  const p = v.bloquantes.find((b) => b.regle === "prealable");
  assert.match(p.message, /IFT2015/);
});

test("un préalable prévu dans la même session ne suffit pas", () => {
  const v = R.verifierAjoutCours("IFT2245", ctx({ cours: ["IFT2015"], projets: [], activites: [] }));
  assert.equal(v.ok, false);
});

test("un cours dont les préalables sont réussis est accepté", () => {
  assert.equal(R.verifierAjoutCours("IFT2015", ctx()).ok, true);
});

test("EX-07 : un cours complet est refusé et des équivalents sont proposés", () => {
  const v = R.verifierAjoutCours("IFT2255", ctx());
  const c = v.bloquantes.find((b) => b.regle === "capacite");
  assert.ok(c);
  assert.match(c.message, /IFT2015/);
});

test("EX-05 : un cours hors programme donne un avertissement mais pas de blocage", () => {
  const v = R.verifierAjoutCours("FINA10200", ctx());
  assert.equal(v.ok, true);
  assert.equal(v.avertissements[0].regle, "hors-programme");
});

test("plafond de crédits", () => {
  const plan = { cours: ["IFT2015", "IFT2035", "IFT2105", "IFT3225", "IFT2905", "COM1500"], projets: [], activites: [] };
  const v = R.verifierAjoutCours("FINA10200", ctx(plan));
  assert.ok(v.bloquantes.some((b) => b.regle === "plafond"));
});

test("échéance : aucun ajout après la date limite de modification", () => {
  const v = R.verifierAjoutCours("IFT2015", ctx(undefined, "2026-09-17"));
  assert.ok(v.bloquantes.some((b) => b.regle === "echeance"));
});

test("EX-08 : deux cours = sous le temps plein", () => {
  const tp = R.etatTempsPlein({ cours: ["IFT2015", "IFT2035"], projets: [], activites: [] }, offre, regles);
  assert.equal(tp.credits, 6);
  assert.equal(tp.sousSeuil, true);
  assert.equal(tp.manque, 6);
});

test("EX-06 : les activités ne rapportent aucun crédit", () => {
  const plan = { cours: ["IFT2015"], projets: [], activites: ["A1", "A2"] };
  assert.equal(R.creditsSession(plan, offre), 3);
});

test("EX-05 : un cours hors programme ne compte dans aucun bloc", () => {
  const prog = R.progressionParBloc({ cours: ["FINA10200"], projets: [], activites: [] }, offre, dossier);
  assert.equal(prog.reduce((s, b) => s + b.prevus, 0), 0);
});

test("projet non admissible si les crédits acquis sont insuffisants", () => {
  const p3 = offre.projets.find((p) => p.id === "P3");
  const a = R.admissibiliteProjet(p3, { dossier, plan: { cours: [], projets: [] }, demandes: [] });
  assert.equal(a.ok, false);
});

test("EX-10 : rappel à J-2, relance unique, puis expiration", () => {
  const p2 = offre.projets.find((p) => p.id === "P2"); // ne répond jamais
  let d = D.creerDemande(p2, "2026-09-08", regles);
  assert.equal(d.echeance, "2026-09-15");
  let r = D.avancerDemande(d, p2, "2026-09-13", regles);
  assert.equal(r.demande.rappelEnvoye, true);
  d = D.relancer(r.demande, regles);
  assert.equal(d.echeance, "2026-09-18");
  assert.throws(() => D.relancer(d, regles));
  r = D.avancerDemande(d, p2, "2026-09-19", regles);
  assert.equal(r.demande.etat, "expiree");
});

test("réponse simulée : acceptation après le délai de l'encadrant", () => {
  const p1 = offre.projets.find((p) => p.id === "P1");
  const d = D.creerDemande(p1, "2026-09-08", regles);
  assert.equal(D.avancerDemande(d, p1, "2026-09-10", regles).demande.etat, "envoyee");
  const r = D.avancerDemande(d, p1, "2026-09-11", regles);
  assert.equal(r.demande.etat, "offerte");
  assert.equal(D.accepterOffre(r.demande).etat, "confirmee");
});
