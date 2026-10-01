"""Évaluation des règles de programme et des conflits (E-05 à E-08).

Les états de règle sont calculés, jamais stockés.
TEMP(règle): quatre types de règles seulement, voir Regle.TYPES.
"""
from .models import Element


def evaluer(programme, elements, inclure_intentions=False):
    """Retourne [(regle, etat, message)] avec etat dans respectee, a_risque, violee."""
    etats = Element.COMPTES + (("intention",) if inclure_intentions else ())
    comptes = [e for e in elements if e.etat in etats]
    total = sum(e.activite.credits for e in comptes)
    resultats = []
    if programme is None:
        return resultats
    for r in programme.regle_set.all():
        if r.type == "max_credits":
            ok = total <= r.valeur
            etat, msg = ("respectee", f"{total} crédits sur {r.valeur} permis") if ok else (
                "violee", f"{total} crédits, plafond de {r.valeur} dépassé")
        elif r.type == "min_credits":
            ok = total >= r.valeur
            etat, msg = ("respectee", f"{total} crédits") if ok else (
                "a_risque", f"{total} crédits, il en manque {r.valeur - total}")
        elif r.type == "temps_plein":
            ok = total >= r.valeur
            etat, msg = ("respectee", f"{total} crédits, temps plein") if ok else (
                "a_risque", f"{total} crédits, sous le seuil de {r.valeur}. {r.consequence}")
        else:  # bloc
            n = sum(e.activite.credits for e in comptes if e.activite.bloc == r.bloc)
            ok = n >= r.valeur
            etat, msg = ("respectee", f"{n} crédits du bloc") if ok else (
                "a_risque", f"{n} crédits du bloc {r.bloc}, il en manque {r.valeur - n}")
        resultats.append((r, etat, msg))
    return resultats


def conflits(profil, session, activite, elements):
    """Motifs qui empêchent d'ajouter l'activité (E-07, E-14)."""
    motifs = []
    if not activite.sessions.filter(pk=session.pk).exists():
        motifs.append(f"Non offerte à la session {session}")
    manquants = activite.prealables.exclude(pk__in=profil.termines.all())
    if manquants:
        motifs.append("Préalables manquants : " + ", ".join(a.titre for a in manquants))
    if activite.horaire:
        for e in elements:
            if e.etat in Element.COMPTES and e.activite.horaire == activite.horaire:
                motifs.append(f"Conflit d'horaire ({activite.horaire}) avec {e.activite.titre}")
    if any(e.activite_id == activite.pk for e in elements):
        motifs.append("Déjà dans le plan")
    return motifs
