from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from planif.models import (Activite, Echeance, Hote, Profil, Programme, Regle,
                           Session)


class Command(BaseCommand):
    help = "TEMP(données): peuple le monde simulé (remplace les données existantes)"

    def handle(self, *a, **kw):
        User.objects.filter(is_superuser=False).delete()
        for m in (Activite, Profil, Hote, Echeance, Session, Regle, Programme):
            m.objects.all().delete()

        prog = Programme.objects.create(nom="Baccalauréat en informatique")
        for type_, valeur, bloc, libelle, cons in [
            ("min_credits", 9, "", "Minimum de crédits", ""),
            ("max_credits", 18, "", "Plafond de crédits", ""),
            ("temps_plein", 12, "", "Seuil de temps plein",
             "Sous ce seuil, prêts et bourses sont à risque."),
            ("bloc", 6, "fondements", "Bloc fondements", ""),
        ]:
            Regle.objects.create(programme=prog, type=type_, valeur=valeur, bloc=bloc,
                                 libelle=libelle, consequence=cons)

        auj = date.today()
        a26, h27, e27, a27 = [
            Session.objects.create(libelle=l, debut=auj + timedelta(days=d), fin=auj + timedelta(days=d + 100))
            for l, d in [("Session en cours", -40), ("Session suivante", 80), ("Session +2", 220),
                         ("Session +3", 360)]]
        for libelle, abandon, jours in [("Abandon sans frais", False, 5), ("Date limite d'abandon", True, 30)]:
            Echeance.objects.create(session=a26, libelle=libelle, abandon=abandon, date=auj + timedelta(days=jours))

        lab_ia = Hote.objects.create(nom="Prof. Tremblay (Labo IA)",
                                     capacite=1, disponibilite_estimee=30)
        prof_g = Hote.objects.create(nom="Prof. Gagnon",
                                     capacite=2, disponibilite_estimee=70)
        nova = Hote.objects.create(nom="Nova Technologies", capacite=3,
                                   disponibilite_estimee=50)

        def act(titre, type_, credits=3, sessions=(a26, h27), **kw):
            a = Activite.objects.create(titre=titre, type=type_, credits=credits,
                                        maj=auj, **kw)
            a.sessions.set(sessions)
            return a

        prog1 = act("IFT1025 Programmation 2", "cours", bloc="fondements", horaire="Mer 9h")
        algebre = act("MAT1978 Algèbre linéaire", "cours", horaire="Jeu 13h")
        gl = act("IFT2255 Génie logiciel", "cours", bloc="fondements", horaire="Lun 9h",
                 sessions=(a26, a27))
        act("IFT2125 Intro à l'algorithmique", "cours", bloc="fondements", horaire="Mar 9h")
        struct = act("IFT2015 Structures de données", "cours", bloc="fondements", horaire="Ven 9h")
        struct.prealables.add(prog1)
        act("IFT2035 Concepts des langages", "cours", horaire="Lun 9h", places=0)  # complet
        act("IFT3000 Bases de données", "cours", horaire="Mar 13h", sessions=(h27, a27))
        act("IFT3150 Projet supervisé IA", "projet", hote=lab_ia, source="Labo IA")
        act("Projet supervisé systèmes", "projet", hote=prof_g, source="Prof. Gagnon")
        act("Poste d'assistance de laboratoire", "poste", credits=3, hote=prof_g,
            source="Prof. Gagnon")
        act("Stage chez Nova", "stage", credits=6, hote=nova, source="Nova Technologies",
            sessions=(e27,))
        act("Séminaire de recherche", "seminaire", credits=1, source="Courriel du département")
        act("Concours de programmation", "concours", credits=1, source="Association étudiante")

        def compte(login):
            # TEMP(données): mot de passe de démonstration identique pour tous
            return User.objects.create_user(login, password="demo")

        alice = Profil.objects.create(user=compte("alice"), nom="Alice (info, 2e année)", programme=prog,
                                      interets="IA, génie logiciel", credits_vises=15)
        alice.termines.set([prog1, algebre])
        Profil.objects.create(user=compte("bob"), nom="Bob (info, 1re année)", programme=prog,
                              interets="systèmes", credits_vises=12)
        Profil.objects.create(user=compte("tremblay"), nom="Prof. Tremblay", role="encadrante", hote=lab_ia)
        Profil.objects.create(user=compte("gagnon"), nom="Prof. Gagnon", role="encadrante", hote=prof_g)
        self.stdout.write("Données de démonstration créées. Comptes alice, bob, tremblay, gagnon (mot de passe : demo).")
