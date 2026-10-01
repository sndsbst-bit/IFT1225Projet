from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.forms import Form, ModelChoiceField, ModelForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import regles
from .models import Activite, Appreciation, Demande, Element, Profil, Session

DELAI_DEMANDE = 14  # jours avant expiration d'une demande
DELAI_ALERTE = 14  # jours avant une échéance pour alerter


def acces(role=None, session=True):
    """Connexion et rôle requis. La vue reçoit le profil et la session courante (date réelle)."""
    def decorateur(vue):
        @wraps(vue)
        @login_required
        def enveloppe(request, *a, **kw):
            profil = Profil.objects.filter(user=request.user).first()
            if profil is None or (role and profil.role != role):
                raise PermissionDenied
            today = timezone.localdate()
            for d in Demande.objects.filter(etat="envoyee", expire_le__lt=today):  # E-10
                d.etat = "expiree"
                d.save()
                if d.element:
                    d.element.delete()
            courante = Session.objects.filter(fin__gte=today).first()  # en cours, sinon la prochaine
            if session and courante is None:
                return render(request, "planif/refus.html", {
                    "titre": "Aucune session", "motifs": ["Aucune session en cours ou à venir."]})
            return vue(request, profil, courante, *a, **kw)
        return enveloppe
    return decorateur


def elements_de(profil, session):
    return list(Element.objects.filter(profil=profil, session=session).select_related("activite"))


def refus(request, titre, motifs):
    return render(request, "planif/refus.html", {"titre": titre, "motifs": motifs})


def avertir(request, titre, motifs):
    return render(request, "planif/avertissement.html", {
        "titre": titre, "motifs": motifs, "action": request.path})


# ---- Profil (CU1) et appréciations (CU10) ----

class ProfilForm(ModelForm):
    class Meta:
        model = Profil
        fields = ["programme", "interets", "preference", "credits_vises"]


@acces("etudiante", session=False)
def profil_page(request, profil, session):
    form = ProfilForm(request.POST or None, instance=profil)
    if form.is_valid():
        form.save()
        messages.success(request, "Profil enregistré.")
        return redirect("profil")
    notes = dict(Appreciation.objects.filter(profil=profil).values_list("activite_id", "note"))
    return render(request, "planif/profil.html", {
        "form": form, "termines": [(a, notes.get(a.pk)) for a in profil.termines.all()]})


class AppreciationForm(ModelForm):
    class Meta:
        model = Appreciation
        fields = ["note"]


@acces("etudiante", session=False)
@require_POST
def apprecier(request, profil, session, pk):
    activite = get_object_or_404(profil.termines, pk=pk)
    existante = Appreciation.objects.filter(profil=profil, activite=activite).first()
    form = AppreciationForm(request.POST, instance=existante or Appreciation(profil=profil, activite=activite))
    if form.is_valid():
        form.save()
    else:
        messages.error(request, "Note invalide (1 à 5).")
    return redirect("profil")


# ---- Plan de la session courante (CU3, CU4, CU7, CU9) ----

@acces(session=False)
def plan(request, profil, session):
    if profil.role == "encadrante":
        return redirect("demandes")
    if session is None:
        return refus(request, "Aucune session", ["Aucune session en cours ou à venir."])
    today = timezone.localdate()
    elements = elements_de(profil, session)
    echeances = session.echeance_set.all()
    return render(request, "planif/plan.html", {
        "session": session, "elements": elements, "echeances": echeances,
        "regles": regles.evaluer(profil.programme, elements),
        "alertes": [e for e in echeances if today <= e.date <= today + timedelta(days=DELAI_ALERTE)],
        "demandes": Demande.objects.filter(profil=profil).select_related("activite", "hote")})


@acces("etudiante")
def catalogue(request, profil, session):
    type_ = request.GET.get("type", "")
    activites = Activite.objects.filter(sessions=session).select_related("hote")
    if type_:
        activites = activites.filter(type=type_)
    mots = [m.strip().lower() for m in profil.interets.split(",") if m.strip()]
    notes = dict(Appreciation.objects.values("activite").annotate(m=Avg("note"))
                 .values_list("activite", "m"))
    liste = []
    for a in activites:  # E-04 : suggestion expliquée
        raisons = [f"correspond à « {m} »" for m in mots if m in a.titre.lower()]
        if notes.get(a.pk, 0) >= 4:
            raisons.append(f"bien appréciée ({notes[a.pk]:.1f}/5)")
        liste.append((a, raisons))
    liste.sort(key=lambda x: -len(x[1]))
    return render(request, "planif/catalogue.html", {
        "session": session, "activites": liste, "types": Activite.TYPES, "type": type_})


@acces("etudiante")
@require_POST
def ajouter(request, profil, session, pk):
    """Flux 1 : conflits, règles avant l'ajout, avertissement confirmé par la personne."""
    activite = get_object_or_404(Activite, pk=pk)
    elements = [e for e in elements_de(profil, session)
                if not (e.activite_id == activite.pk and e.etat == "intention")]
    motifs = regles.conflits(profil, session, activite, elements)
    if motifs:
        return refus(request, activite.titre, motifs)

    candidat = Element(profil=profil, session=session, activite=activite,
                       etat="demande" if activite.hote else "offert")
    resultats = regles.evaluer(profil.programme, elements + [candidat])
    violees = [m for _, s, m in resultats if s == "violee"]
    if violees:
        return refus(request, activite.titre, violees)
    risques = [m for _, s, m in resultats if s == "a_risque"]
    if risques and not request.POST.get("confirmer"):
        return avertir(request, f"Ajouter {activite.titre}", risques)

    hote = activite.hote
    if hote and Demande.objects.filter(hote=hote, etat__in=["envoyee", "acceptee"]).count() >= hote.capacite:
        return refus(request, activite.titre, [f"{hote} a atteint sa capacité"])  # CU5
    with transaction.atomic():
        Element.objects.filter(profil=profil, session=session, activite=activite).delete()  # intention
        candidat.save()
        if hote:
            Demande.objects.create(
                element=candidat, profil=profil, activite=activite, hote=hote,
                expire_le=timezone.localdate() + timedelta(days=DELAI_DEMANDE))
    messages.success(request, f"{activite.titre} ajouté ({candidat.get_etat_display()}).")
    return redirect("plan")


@acces("etudiante")
@require_POST
def retirer(request, profil, session, pk):
    """Flux 4 : retrait soumis à la date limite d'abandon."""
    e = get_object_or_404(Element, pk=pk, profil=profil)
    abandon = e.session.echeance_set.filter(abandon=True).first()
    if abandon and timezone.localdate() > abandon.date and not request.POST.get("confirmer"):
        return avertir(request, f"Retirer {e.activite.titre}",
                       [f"Date limite d'abandon passée ({abandon.date}) : frais possibles."])
    if e.etat == "confirme":
        e.activite.places += 1
        e.activite.save()
    Demande.objects.filter(element=e).update(etat="refusee")
    e.delete()
    messages.success(request, "Activité retirée.")
    return redirect("plan")


@acces("etudiante")
@require_POST
def soumettre(request, profil, session):
    """Flux 3 : TEMP(registrariat) validation simulée, rejet avec motif."""
    elements = elements_de(profil, session)
    motifs = [m for _, s, m in regles.evaluer(profil.programme, elements) if s == "violee"]
    a_valider = [e for e in elements if e.etat == "offert"]
    motifs += [f"Registrariat : {e.activite.titre} est complet" for e in a_valider
               if e.activite.places <= 0]
    if motifs or not a_valider:
        return refus(request, "Soumission refusée", motifs or ["Rien à soumettre"])
    with transaction.atomic():
        for e in a_valider:
            e.etat = "confirme"
            e.save()
            e.activite.places -= 1
            e.activite.save()
    messages.success(request, "Plan accepté par le registrariat (simulé).")
    return redirect("plan")


# ---- Personne qui encadre (CU6) ----

@acces("encadrante", session=False)
def demandes(request, profil, session):
    return render(request, "planif/demandes.html", {
        "hote": profil.hote,
        "demandes": Demande.objects.filter(hote=profil.hote).select_related("profil", "activite")})


@acces("encadrante", session=False)
@require_POST
def repondre(request, profil, session, pk):
    d = get_object_or_404(Demande, pk=pk, hote=profil.hote, etat="envoyee")
    reponse = request.POST.get("reponse")
    if reponse not in ("accepter", "refuser"):
        return HttpResponseBadRequest("Réponse invalide")
    d.etat = "acceptee" if reponse == "accepter" else "refusee"
    d.save()
    if reponse == "accepter":
        d.element.etat = "offert"
        d.element.save()
    else:
        d.element.delete()  # libère la place
    return redirect("demandes")


# ---- Vue multi-sessions (CU8) ----

class IntentionForm(Form):
    activite = ModelChoiceField(Activite.objects.all())
    session = ModelChoiceField(Session.objects.all())


@acces("etudiante", session=False)
def multisession(request, profil, session):
    if request.method == "POST":
        form = IntentionForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Choix invalide.")
            return redirect("multisession")
        s, activite = form.cleaned_data["session"], form.cleaned_data["activite"]
        # Une intention ne réserve rien : seuls l'offre et le doublon bloquent ici.
        if not activite.sessions.filter(pk=s.pk).exists():
            messages.error(request, f"{activite.titre} n'est pas offerte à la session {s}.")
        else:
            Element.objects.create(profil=profil, session=s, activite=activite, etat="intention")
        return redirect("multisession")
    colonnes = []
    for s in Session.objects.all():
        elements = elements_de(profil, s)
        colonnes.append({"session": s, "elements": elements,
                         "regles": regles.evaluer(profil.programme, elements, inclure_intentions=True)})
    return render(request, "planif/multisession.html", {
        "colonnes": colonnes, "activites": Activite.objects.all()})


@acces("etudiante", session=False)
@require_POST
def retirer_intention(request, profil, session, pk):
    get_object_or_404(Element, pk=pk, profil=profil, etat="intention").delete()
    return redirect("multisession")
