// Interface (conteneur « Application web » du C4). Affiche l'état et relaie les actions à l'API simulée.

import * as API from "./api.js";
import * as R from "./regles.js";
import { joursRestants, LIBELLES_ETAT } from "./demandes.js";

let donnees;
let etat;
let onglet = "cours";

const $ = (id) => document.getElementById(id);

// ---------- Rendu ----------

function afficherMessage(html, type) {
  $("message").innerHTML = html ? `<div class="boite ${type}">${html}</div>` : "";
}

function rendreOffre() {
  const filtre = $("recherche").value.trim().toLowerCase();
  const correspond = (...champs) => !filtre || champs.join(" ").toLowerCase().includes(filtre);
  const reussis = R.coursReussis(etat.dossier);
  let html = "";

  if (onglet === "cours") {
    for (const c of etat.offre.cours.filter((c) => correspond(c.code, c.titre))) {
      const dansPlan = etat.plan.cours.includes(c.code);
      const complet = c.inscrits >= c.places;
      const prereq = c.prealables.length ? `Préalables : ${c.prealables.map((p) => (reussis.has(p) ? `${p} ✓` : `${p} ✗`)).join(", ")}` : "Aucun préalable";
      html += `
        <div class="element">
          <div>
            <div class="titre">${c.code} — ${c.titre}</div>
            <div class="details">
              <span class="etiquette">${c.credits} cr.</span>
              <span class="etiquette ${c.bloc === "hors" ? "hors" : ""}">${nomBloc(c.bloc)}</span>
              <span class="etiquette ${complet ? "complet" : ""}">${complet ? "Complet" : `${c.places - c.inscrits} places`}</span>
              <br>${prereq}
            </div>
          </div>
          <button class="btn" data-action="ajouter-cours" data-id="${c.code}" ${dansPlan ? "disabled" : ""}>${dansPlan ? "Dans le plan" : "Ajouter"}</button>
        </div>`;
    }
  }

  if (onglet === "projets") {
    for (const p of etat.offre.projets.filter((p) => correspond(p.titre, p.domaine, p.encadrant))) {
      const i = p.indicateur;
      html += `
        <div class="element">
          <div>
            <div class="titre">${p.titre}</div>
            <div class="details">
              ${p.encadrant} · ${p.domaine}<br>
              <span class="etiquette">${p.credits} cr.</span>
              <span class="etiquette">${p.places - p.inscrits} place(s)</span>
              <span class="etiquette">Min. ${p.creditsMinimum} cr. acquis</span><br>
              <span title="Indicateur agrégé (EX-11)">📊 ${i.demandesEnAttente} demande(s) en attente · délai habituel ≈ ${i.delaiHabituelJours} j</span>
            </div>
          </div>
          <button class="btn" data-action="demander" data-id="${p.id}">Envoyer une demande</button>
        </div>`;
    }
  }

  if (onglet === "activites") {
    for (const a of etat.offre.activites.filter((a) => correspond(a.titre, a.type))) {
      const dansPlan = etat.plan.activites.includes(a.id);
      const complet = a.inscrits >= a.places;
      html += `
        <div class="element">
          <div>
            <div class="titre">${a.titre}</div>
            <div class="details">
              <span class="etiquette">${a.type}</span>
              <span class="etiquette zero">0 crédit</span>
              <span class="etiquette ${complet ? "complet" : ""}">${complet ? "Complet" : `${a.places - a.inscrits} places`}</span>
            </div>
          </div>
          <button class="btn" data-action="ajouter-activite" data-id="${a.id}" ${dansPlan || complet ? "disabled" : ""}>${dansPlan ? "Ajoutée" : "Ajouter"}</button>
        </div>`;
    }
  }

  $("liste-offre").innerHTML = html || `<p class="vide">Aucun élément ne correspond au filtre.</p>`;
}

function nomBloc(id) {
  if (id === "hors") return "Hors programme";
  return etat.dossier.blocs.find((b) => b.id === id)?.nom ?? id;
}

function rendrePlan() {
  const { offre, plan } = etat;
  let html = "";
  for (const code of plan.cours) {
    const c = offre.cours.find((x) => x.code === code);
    html += `<div class="element"><div><div class="titre">${c.code} — ${c.titre}</div>
      <div class="details"><span class="etiquette">${c.credits} cr.</span><span class="etiquette ${c.bloc === "hors" ? "hors" : ""}">${nomBloc(c.bloc)}</span> État : prévu</div></div>
      <button class="btn" data-action="retirer-cours" data-id="${c.code}">Retirer</button></div>`;
  }
  for (const id of plan.projets) {
    const p = offre.projets.find((x) => x.id === id);
    html += `<div class="element"><div><div class="titre">Projet — ${p.titre}</div>
      <div class="details"><span class="etiquette">${p.credits} cr.</span> ${p.encadrant} · État : confirmé</div></div></div>`;
  }
  for (const id of plan.activites) {
    const a = offre.activites.find((x) => x.id === id);
    html += `<div class="element"><div><div class="titre">${a.titre}</div>
      <div class="details"><span class="etiquette zero">0 crédit</span> Activité facultative : ne compte pas dans le programme</div></div>
      <button class="btn" data-action="retirer-activite" data-id="${a.id}">Retirer</button></div>`;
  }
  $("plan").innerHTML = html || `<p class="vide">Votre plan est vide. Ajoutez des cours depuis l'offre.</p>`;

  // EX-08 : état du temps plein, visible en permanence.
  const tp = R.etatTempsPlein(plan, offre, etat.regles);
  $("temps-plein").innerHTML = tp.sousSeuil
    ? `<div class="boite alerte"><strong>${tp.credits} crédits : sous le temps plein (${tp.seuil} cr.)</strong>Il manque ${tp.manque} crédits. ${etat.regles.consequenceTempsPartiel}</div>`
    : `<div class="boite succes"><strong>${tp.credits} crédits : temps plein</strong>Plafond : ${etat.regles.plafondCredits} crédits.</div>`;

  // EX-01 / EX-06 : progression par bloc.
  $("progression").innerHTML = R.progressionParBloc(plan, offre, etat.dossier).map((b) => {
    const pa = (100 * b.acquis) / b.credits;
    const pp = (100 * Math.min(b.prevus, b.credits - b.acquis)) / b.credits;
    return `<div class="bloc"><div class="bloc-entete"><span>${b.nom}</span><span>${b.acquis} acquis + ${b.prevus} prévus / ${b.credits}</span></div>
      <div class="barre"><div class="acquis" style="width:${pa}%"></div><div class="prevus" style="width:${pp}%"></div></div></div>`;
  }).join("");

  $("confirmer").textContent = plan.confirme ? "Plan confirmé ✓" : "Confirmer le plan";
  $("confirmer").disabled = plan.confirme || (plan.cours.length === 0 && plan.projets.length === 0);
}

function rendreDemandes() {
  if (etat.demandes.length === 0) {
    $("demandes").innerHTML = `<p class="vide">Aucune demande. Voir l'onglet « Projets supervisés ».</p>`;
    return;
  }
  $("demandes").innerHTML = etat.demandes.map((d) => {
    const p = etat.offre.projets.find((x) => x.id === d.projetId);
    let detail = "";
    let actions = "";
    if (d.etat === "envoyee") {
      const reste = joursRestants(d, etat.date);
      detail = `Délai de réponse : ${d.echeance} (${reste} j restant${reste > 1 ? "s" : ""})${d.relancee ? " · déjà relancée" : ""}`;
      if (d.rappelEnvoye) {
        actions = `${d.relancee ? "" : `<button class="btn" data-action="relancer" data-id="${d.id}">Relancer</button>`}
          <button class="btn" data-action="rediriger" data-id="${d.id}">Choisir une autre offre</button>`;
      }
    } else if (d.etat === "offerte") {
      detail = "L'encadrant·e propose une entente.";
      actions = `<button class="btn btn-principal" data-action="accepter" data-id="${d.id}">Accepter l'entente</button>`;
    } else {
      detail = d.motif;
    }
    const type = { expiree: "erreur", refusee: "erreur", retiree: "erreur", confirmee: "succes", offerte: "succes" }[d.etat] ?? (d.rappelEnvoye ? "rappel" : "");
    return `<div class="element"><div><div class="titre">${p.titre}</div>
      <div class="details">${p.encadrant} · <span class="boite ${type}" style="padding:1px 6px">${LIBELLES_ETAT[d.etat]}</span><br>${detail}</div></div>
      <div class="actions">${actions}</div></div>`;
  }).join("");
}

function rendreEntete() {
  $("date").textContent = etat.date;
  $("session").textContent = etat.regles.session;
  $("profil").textContent = `${etat.dossier.nom} · ${etat.dossier.programme} · ${R.creditsAcquis(etat.dossier)} crédits acquis (dossier ${etat.dossier.source})`;
  const r = etat.regles;
  $("bandeau-echeance").textContent =
    etat.date <= r.dateLimiteModification
      ? `Échéance : modification du choix de cours jusqu'au ${r.dateLimiteModification} (sans frais). Ensuite, plus d'ajout possible.`
      : `Date limite de modification passée. Abandon avec frais possible jusqu'au ${r.dateLimiteAbandon} (mention au relevé).`;
}

function rendreJournal() {
  $("journal").innerHTML = etat.journal.map((j) => `<li class="${j.type}"><span class="d">${j.date}</span>${j.texte}</li>`).join("");
}

function rendre() {
  rendreEntete();
  rendreOffre();
  rendrePlan();
  rendreDemandes();
  rendreJournal();
  document.querySelectorAll(".onglet").forEach((b) => b.classList.toggle("actif", b.dataset.onglet === onglet));
}

// ---------- Actions ----------

function liste(items) {
  return `<ul>${items.map((i) => `<li>${i.message}</li>`).join("")}</ul>`;
}

const actions = {
  "ajouter-cours"(code) {
    const v = API.ajouterCours(etat, code);
    if (!v.ok) afficherMessage(`<strong>Ajout de ${code} refusé</strong>${liste(v.bloquantes)}`, "erreur");
    else if (v.avertissements.length) afficherMessage(`<strong>${code} ajouté, avec avertissement</strong>${liste(v.avertissements)}`, "alerte");
    else afficherMessage(`<strong>${code} ajouté au plan</strong>`, "succes");
  },
  "retirer-cours"(code) { API.retirerCours(etat, code); afficherMessage(""); },
  "ajouter-activite"(id) {
    const r = API.ajouterActivite(etat, id);
    afficherMessage(r.ok ? "<strong>Activité ajoutée</strong>Elle ne rapporte aucun crédit." : r.message, r.ok ? "rappel" : "erreur");
  },
  "retirer-activite"(id) { API.retirerActivite(etat, id); },
  demander(id) {
    const r = API.envoyerDemande(etat, id);
    afficherMessage(r.ok
      ? `<strong>Demande envoyée</strong>Réponse attendue au plus tard le ${r.demande.echeance}. Utilisez « Avancer d'un jour » pour simuler l'attente.`
      : `<strong>Demande impossible</strong>${r.message}`, r.ok ? "succes" : "erreur");
  },
  relancer(id) { API.relancerDemande(etat, id); afficherMessage("<strong>Relance envoyée</strong>Le délai est prolongé. Une seule relance est permise.", "rappel"); },
  rediriger(id) {
    const s = API.redirigerDemande(etat, id);
    onglet = "projets";
    afficherMessage(`<strong>Demande retirée</strong>${s.length ? `Offres équivalentes accessibles :${liste(s.map((p) => ({ message: `${p.titre} (${p.encadrant}, délai habituel ≈ ${p.indicateur.delaiHabituelJours} j)` })))}` : "Aucune offre équivalente."}`, "rappel");
  },
  accepter(id) { API.accepterOffre(etat, id); afficherMessage("<strong>Projet confirmé</strong>Il compte maintenant dans vos crédits.", "succes"); },
};

function confirmer() {
  const r = API.confirmerPlan(etat);
  if (r.ok) { afficherMessage("<strong>Plan confirmé</strong>Prochaine étape : l'inscription officielle dans Synchro.", "succes"); rendre(); return; }
  const tp = r.avertissement;
  $("dialogue-texte").textContent = `Votre plan compte ${tp.credits} crédits, sous le seuil de ${tp.seuil}. ${etat.regles.consequenceTempsPartiel}`;
  $("compris").checked = false;
  $("dialogue-confirmer").disabled = true;
  $("dialogue-temps-plein").showModal();
}

// ---------- Démarrage ----------

function brancher() {
  document.body.addEventListener("click", (e) => {
    const b = e.target.closest("[data-action]");
    if (!b) return;
    actions[b.dataset.action](b.dataset.id);
    rendre();
  });
  document.querySelectorAll(".onglet").forEach((b) =>
    b.addEventListener("click", () => { onglet = b.dataset.onglet; afficherMessage(""); rendre(); })
  );
  $("recherche").addEventListener("input", rendreOffre);
  $("avancer").addEventListener("click", () => { API.avancerUnJour(etat); rendre(); });
  $("reinitialiser").addEventListener("click", () => { etat = API.creerEtat(donnees); afficherMessage(""); rendre(); });
  $("confirmer").addEventListener("click", confirmer);
  $("compris").addEventListener("change", (e) => { $("dialogue-confirmer").disabled = !e.target.checked; });
  $("dialogue-temps-plein").addEventListener("close", () => {
    if ($("dialogue-temps-plein").returnValue === "confirmer") {
      API.confirmerPlan(etat, { accepteTempsPartiel: true });
      afficherMessage("<strong>Plan confirmé en temps partiel</strong>Vous avez accepté la conséquence.", "alerte");
    }
    rendre();
  });
}

try {
  donnees = await API.chargerDonnees();
  etat = API.creerEtat(donnees);
  brancher();
  rendre();
} catch (err) {
  document.body.innerHTML = `<div class="boite erreur" style="margin:24px"><strong>Impossible de charger les données.</strong>
    Lancez un serveur local dans le dossier prototype (<code>python3 -m http.server 8000</code>) puis ouvrez http://localhost:8000.<br>${err.message}</div>`;
}
