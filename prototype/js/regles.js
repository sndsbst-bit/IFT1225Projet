// Moteur de règles (conteneur « Moteur de règles » du C4, niveau 2).
// Fonctions pures : elles ne touchent ni au DOM ni à l'état global,
// ce qui permet de les tester avec `node --test` (voir tests/).

/** Codes des cours réussis au dossier. */
export function coursReussis(dossier) {
  return new Set(dossier.coursReussis.map((c) => c.code));
}

/** Crédits acquis au dossier, par bloc du programme. */
export function creditsAcquisParBloc(dossier) {
  const parBloc = {};
  for (const b of dossier.blocs) parBloc[b.id] = 0;
  for (const c of dossier.coursReussis) parBloc[c.bloc] = (parBloc[c.bloc] ?? 0) + c.credits;
  return parBloc;
}

export function creditsAcquis(dossier) {
  return dossier.coursReussis.reduce((s, c) => s + c.credits, 0);
}

/**
 * Éléments crédités du plan (EX-06) : cours prévus et projets confirmés.
 * Les activités (visites, séminaires, concours) n'y figurent jamais.
 */
export function elementsCredites(plan, offre) {
  const cours = plan.cours.map((code) => offre.cours.find((c) => c.code === code));
  const projets = plan.projets.map((id) => offre.projets.find((p) => p.id === id));
  return [...cours, ...projets].filter(Boolean);
}

/** Crédits de la session : ce qui compte pour le temps plein et le plafond. */
export function creditsSession(plan, offre) {
  return elementsCredites(plan, offre).reduce((s, e) => s + e.credits, 0);
}

/**
 * Progression dans le programme après la session (EX-01, EX-05, EX-06).
 * Les cours hors programme ne comptent dans aucun bloc.
 * Les projets sont rangés dans le bloc « options » (simplification assumée).
 */
export function progressionParBloc(plan, offre, dossier) {
  const acquis = creditsAcquisParBloc(dossier);
  const prevus = {};
  for (const b of dossier.blocs) prevus[b.id] = 0;
  for (const code of plan.cours) {
    const c = offre.cours.find((x) => x.code === code);
    if (c && c.bloc in prevus) prevus[c.bloc] += c.credits;
  }
  for (const id of plan.projets) {
    const p = offre.projets.find((x) => x.id === id);
    if (p) prevus.options += p.credits;
  }
  return dossier.blocs.map((b) => ({
    ...b,
    acquis: acquis[b.id] ?? 0,
    prevus: prevus[b.id] ?? 0,
  }));
}

/** EX-08 : état du plan par rapport au seuil de temps plein. */
export function etatTempsPlein(plan, offre, regles) {
  const credits = creditsSession(plan, offre);
  return {
    credits,
    seuil: regles.seuilTempsPlein,
    sousSeuil: credits < regles.seuilTempsPlein,
    manque: Math.max(0, regles.seuilTempsPlein - credits),
  };
}

/**
 * Vérifie l'ajout d'un cours au plan (CU03 + CU04, flux F1).
 * Retourne { ok, bloquantes: [{regle, message}], avertissements: [...] }.
 * Un seul manquement bloquant suffit à refuser l'ajout.
 */
export function verifierAjoutCours(code, { plan, offre, dossier, regles, date }) {
  const bloquantes = [];
  const avertissements = [];
  const cours = offre.cours.find((c) => c.code === code);

  if (!cours) {
    return { ok: false, bloquantes: [{ regle: "inconnu", message: `Le cours ${code} n'est pas offert cette session.` }], avertissements };
  }
  if (plan.cours.includes(code)) {
    bloquantes.push({ regle: "doublon", message: `${code} est déjà dans votre plan.` });
  }
  if (coursReussis(dossier).has(code)) {
    bloquantes.push({ regle: "deja-reussi", message: `${code} figure déjà à votre dossier comme réussi.` });
  }

  // Échéance (SIM-10) : après la date limite de modification, on ne peut plus ajouter de cours.
  if (date > regles.dateLimiteModification) {
    bloquantes.push({
      regle: "echeance",
      message: `La date limite de modification (${regles.dateLimiteModification}) est passée : l'ajout d'un cours n'est plus possible.`,
    });
  }

  // EX-03 : préalables. Un préalable prévu dans la même session ne compte pas.
  const reussis = coursReussis(dossier);
  const manquants = cours.prealables.filter((p) => !reussis.has(p));
  if (manquants.length > 0) {
    const detail = manquants
      .map((p) => {
        const offert = offre.cours.find((c) => c.code === p);
        return offert ? `${p} (offert cette session)` : p;
      })
      .join(", ");
    bloquantes.push({
      regle: "prealable",
      message: `Préalable manquant pour ${code} : ${detail}. Planifiez-le d'abord ; vous pourrez suivre ${code} à une session suivante.`,
    });
  }

  // EX-07 : capacité ferme.
  if (cours.inscrits >= cours.places) {
    const equivalents = offre.cours
      .filter((c) => c.bloc === cours.bloc && c.code !== code && c.inscrits < c.places && !plan.cours.includes(c.code))
      .filter((c) => c.prealables.every((p) => reussis.has(p)) && !reussis.has(c.code))
      .map((c) => c.code);
    bloquantes.push({
      regle: "capacite",
      message: `${code} est complet (${cours.inscrits}/${cours.places}).` +
        (equivalents.length ? ` Cours du même bloc encore ouverts : ${equivalents.join(", ")}.` : ""),
    });
  }

  // Plafond de crédits.
  const apres = creditsSession(plan, offre) + cours.credits;
  if (apres > regles.plafondCredits) {
    bloquantes.push({
      regle: "plafond",
      message: `Avec ${code}, votre session atteindrait ${apres} crédits, au-delà du plafond de ${regles.plafondCredits}.`,
    });
  }

  // EX-05 : cours hors programme (avertissement, pas un blocage).
  if (cours.bloc === "hors") {
    avertissements.push({
      regle: "hors-programme",
      message: `${code} ne compte dans aucun bloc de votre programme. ${cours.autorisation ?? "Une autorisation est requise"}.`,
    });
  }

  return { ok: bloquantes.length === 0, bloquantes, avertissements };
}

/** Admissibilité à un projet supervisé (flux F2, première décision). */
export function admissibiliteProjet(projet, { dossier, plan, demandes }) {
  const acquis = creditsAcquis(dossier);
  if (acquis < projet.creditsMinimum) {
    return { ok: false, message: `Il faut ${projet.creditsMinimum} crédits acquis pour ce projet ; vous en avez ${acquis}.` };
  }
  if (projet.inscrits >= projet.places) {
    return { ok: false, message: "Ce projet n'a plus de place." };
  }
  if (plan.projets.length > 0) {
    return { ok: false, message: "Vous avez déjà un projet confirmé cette session." };
  }
  if (demandes.some((d) => d.projetId === projet.id && ["envoyee", "offerte"].includes(d.etat))) {
    return { ok: false, message: "Une demande pour ce projet est déjà en cours." };
  }
  return { ok: true, message: "" };
}
