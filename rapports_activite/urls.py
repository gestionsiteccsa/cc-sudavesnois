from django.urls import path

from . import views

app_name = "rapports_activite"

urlpatterns = [
    # Page publique
    path("rapports-activite/", views.rapports_activite, name="rapports_activite"),
    # Page d'ajout de rapport d'activité
    path(
        "adminccsa/rapports-activite/ajouter/",
        views.add_rapport_activite,
        name="add_rapport_activite",
    ),
    # Page de gestion des rapports d'activité
    path(
        "adminccsa/rapports-activite/gestion/",
        views.manage_rapports_activite,
        name="gestion_rapports_activite",
    ),
    # Page de modification d'un rapport d'activité
    path(
        "adminccsa/rapports-activite/modifier/<int:id>/",
        views.edit_rapport_activite,
        name="edit_rapport_activite",
    ),
    # Page de suppression d'un rapport d'activité
    path(
        "adminccsa/rapports-activite/supprimer/<int:id>/",
        views.delete_rapport_activite,
        name="delete_rapport_activite",
    ),
]
