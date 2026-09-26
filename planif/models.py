from django.conf import settings
from django.db import models


# Modèle du domaine : docs/03-modele-domaine.md.
# TEMP(modèle): les spécialisations d'Activite (cours, projet, poste, stage, séminaire,
# concours) sont aplaties en un seul champ `type`.

class Programme(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Regle(models.Model):
    """Exigence de programme stockée comme donnée (N-02)."""
    TYPES = [("min_credits", "Minimum de crédits"), ("max_credits", "Plafond de crédits"),
             ("temps_plein", "Seuil de temps plein"), ("bloc", "Bloc obligatoire")]
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPES)
    valeur = models.IntegerField()
    bloc = models.CharField(max_length=50, blank=True)
    libelle = models.CharField(max_length=150)
    consequence = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.libelle


class Hote(models.Model):
    """Superviseur, laboratoire ou organisation."""
    nom = models.CharField(max_length=100)
    capacite = models.IntegerField(default=1)
    # TEMP(données): disponibilité = un pourcentage estimé, pas un vrai calendrier
    disponibilite_estimee = models.IntegerField(default=50)

    def __str__(self):
        return self.nom


class Session(models.Model):
    libelle = models.CharField(max_length=50)
    debut = models.DateField()
    fin = models.DateField()

    class Meta:
        ordering = ["debut"]

    def __str__(self):
        return self.libelle


class Echeance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    abandon = models.BooleanField(default=False)  # date limite d'abandon
    libelle = models.CharField(max_length=100)
    date = models.DateField()

    class Meta:
        ordering = ["date"]


class Activite(models.Model):
    TYPES = [("cours", "Cours"), ("projet", "Projet supervisé"), ("poste", "Poste en laboratoire"),
             ("stage", "Stage"), ("seminaire", "Séminaire"), ("concours", "Concours")]
    type = models.CharField(max_length=20, choices=TYPES)
    titre = models.CharField(max_length=150)
    credits = models.IntegerField(default=3)
    places = models.IntegerField(default=30)
    source = models.CharField(max_length=100, default="Répertoire des cours")
    maj = models.DateField(null=True, blank=True)
    hote = models.ForeignKey(Hote, null=True, blank=True, on_delete=models.SET_NULL)
    bloc = models.CharField(max_length=50, blank=True)
    # TEMP(données): horaire = un seul créneau texte, un conflit = même texte
    horaire = models.CharField(max_length=30, blank=True)
    prealables = models.ManyToManyField("self", symmetrical=False, blank=True)
    sessions = models.ManyToManyField(Session, blank=True)  # sessions où l'activité est offerte

    def __str__(self):
        return self.titre


class Profil(models.Model):
    # TEMP(modèle): Personne et Profil du domaine fusionnés en une table
    ROLES = [("etudiante", "Personne étudiante"), ("encadrante", "Personne qui encadre")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLES, default="etudiante")
    programme = models.ForeignKey(Programme, null=True, blank=True, on_delete=models.SET_NULL)
    hote = models.ForeignKey(Hote, null=True, blank=True, on_delete=models.SET_NULL)
    interets = models.CharField("Intérêts (séparés par des virgules)", max_length=200, blank=True)
    preference = models.CharField(max_length=30, blank=True, choices=[
        ("theorie", "Théorie"), ("pratique", "Pratique"), ("recherche", "Recherche"),
        ("industrie", "Industrie")])
    credits_vises = models.IntegerField(default=12)
    termines = models.ManyToManyField(Activite, blank=True, related_name="+")

    def __str__(self):
        return self.nom


class Element(models.Model):
    """Case du plan d'une personne pour une session (Plan du domaine = ces éléments groupés)."""
    ETATS = [("offert", "Offert"), ("demande", "Demande envoyée"), ("confirme", "Confirmé"),
             ("intention", "Intention (aucune place réservée)")]
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    etat = models.CharField(max_length=20, choices=ETATS)

    # Seuls ces états comptent dans les crédits : une intention n'est jamais une place (E-16).
    COMPTES = ("offert", "demande", "confirme")

    class Meta:
        unique_together = ("profil", "session", "activite")


class Demande(models.Model):
    ETATS = [("envoyee", "Envoyée"), ("acceptee", "Acceptée"), ("refusee", "Refusée"),
             ("expiree", "Expirée")]
    # element est vidé quand la demande est refusée ou expirée (la place est libérée)
    element = models.OneToOneField(Element, null=True, on_delete=models.SET_NULL)
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    hote = models.ForeignKey(Hote, on_delete=models.CASCADE)
    etat = models.CharField(max_length=20, choices=ETATS, default="envoyee")
    expire_le = models.DateField()


class Appreciation(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    note = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ("profil", "activite")
