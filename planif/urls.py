from django.contrib.auth import views as auth
from django.urls import path

from . import views

urlpatterns = [
    path("", auth.LoginView.as_view(template_name="planif/login.html", redirect_authenticated_user=True), name="accueil"),
    path("deconnexion/", auth.LogoutView.as_view(), name="deconnexion"),
    path("profil/", views.profil_page, name="profil"),
    path("apprecier/<int:pk>/", views.apprecier, name="apprecier"),
    path("plan/", views.plan, name="plan"),
    path("catalogue/", views.catalogue, name="catalogue"),
    path("ajouter/<int:pk>/", views.ajouter, name="ajouter"),
    path("retirer/<int:pk>/", views.retirer, name="retirer"),
    path("soumettre/", views.soumettre, name="soumettre"),
    path("demandes/", views.demandes, name="demandes"),
    path("repondre/<int:pk>/", views.repondre, name="repondre"),
    path("multisession/", views.multisession, name="multisession"),
    path("intention/<int:pk>/retirer/", views.retirer_intention, name="retirer_intention"),
]
