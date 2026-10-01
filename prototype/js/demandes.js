// Cycle de vie d'une demande de projet supervisé (CU05, CU06, CU07 ; flux F2).
// Dans le système visé, l'avancement du temps est fait par l'« Ordonnanceur » (C4 niveau 2).
// Fonctions pures : chaque fonction renvoie une nouvelle demande au lieu de la modifier.
//
// États : envoyee → offerte → confirmee
//                 ↘ refusee | expiree | retiree

export function ajouterJours(dateIso, n) {
  const d = new Date(dateIso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

export function joursEntre(debutIso, finIso) {
  const ms = new Date(finIso + "T12:00:00Z") - new Date(debutIso + "T12:00:00Z");
  return Math.round(ms / 86400000);
}

let compteur = 0;

export function creerDemande(projet, date, regles) {
  compteur += 1;
  return {
    id: `D${compteur}`,
    projetId: projet.id,
    etat: "envoyee",
    envoyeeLe: date,
    echeance: ajouterJours(date, regles.delaiReponseJours),
    relancee: false,
    rappelEnvoye: false,
    motif: "",
  };
}

/** Jours restants avant l'échéance (négatif si dépassée). */
export function joursRestants(demande, date) {
  return joursEntre(date, demande.echeance);
}

/**
 * Fait avancer une demande au jour `date`.
 * Retourne { demande, evenement } ; `evenement` est un texte à journaliser, ou null.
 */
export function avancerDemande(demande, projet, date, regles) {
  if (demande.etat !== "envoyee") return { demande, evenement: null };

  // Réponse simulée de la personne qui encadre (null = ne répond jamais).
  const rep = projet.reponseSimulee;
  if (rep && joursEntre(demande.envoyeeLe, date) >= rep.apresJours && date <= demande.echeance) {
    if (rep.decision === "accepte") {
      return {
        demande: { ...demande, etat: "offerte" },
        evenement: `${projet.encadrant} accepte votre demande pour « ${projet.titre} ».`,
      };
    }
    return {
      demande: { ...demande, etat: "refusee", motif: "Places réservées à des personnes ayant suivi IFT3395." },
      evenement: `${projet.encadrant} refuse votre demande pour « ${projet.titre} ».`,
    };
  }

  // Échéance dépassée : la demande expire (SIM-08 : ici, jamais en silence).
  if (date > demande.echeance) {
    return {
      demande: { ...demande, etat: "expiree", motif: "Aucune réponse dans le délai." },
      evenement: `Votre demande pour « ${projet.titre} » a expiré sans réponse. Vous êtes libre d'en envoyer une autre.`,
    };
  }

  // Rappel J-2 : on propose de relancer ou de rediriger (CU06).
  if (!demande.rappelEnvoye && joursRestants(demande, date) <= regles.rappelAvantJours) {
    return {
      demande: { ...demande, rappelEnvoye: true },
      evenement: `Rappel : ${projet.encadrant} n'a pas répondu et le délai se termine le ${demande.echeance}. Relancez ou choisissez une autre offre.`,
    };
  }

  return { demande, evenement: null };
}

/** CU06 — relance unique : prolonge le délai. */
export function relancer(demande, regles) {
  if (demande.etat !== "envoyee") throw new Error("Seule une demande en attente peut être relancée.");
  if (demande.relancee) throw new Error("Une seule relance est permise par demande.");
  return {
    ...demande,
    relancee: true,
    rappelEnvoye: false,
    echeance: ajouterJours(demande.echeance, regles.prolongationRelanceJours),
  };
}

/** CU06 — redirection : retire la demande. Les offres équivalentes sont calculées par l'appelant. */
export function retirer(demande) {
  if (demande.etat !== "envoyee") throw new Error("Seule une demande en attente peut être retirée.");
  return { ...demande, etat: "retiree", motif: "Retirée par la personne étudiante." };
}

/** L'étudiante accepte l'offre ; l'approbation du conseil de programme est simulée. */
export function accepterOffre(demande) {
  if (demande.etat !== "offerte") throw new Error("Aucune offre à accepter.");
  return { ...demande, etat: "confirmee" };
}

export const LIBELLES_ETAT = {
  envoyee: "En attente de réponse",
  offerte: "Offre reçue",
  confirmee: "Confirmée",
  refusee: "Refusée",
  expiree: "Expirée",
  retiree: "Retirée",
};
