from django.urls import path

from . import views

app_name = "competences"  # Ajout du namespace

urlpatterns = [
    path("competences/", views.competences, name="competences"),
    # Partie administration
    path(
        "adminccsa/competences/liste/",
        views.competences_list,
        name="admin_competences_list",
    ),
    path("adminccsa/competences/ajouter/", views.add_competence, name="add_competence"),
    path(
        "adminccsa/competences/modifier/<int:competence_id>/",
        views.edit_competence,
        name="edit_competence",
    ),
    path(
        "adminccsa/competences/supprimer/<int:competence_id>/",
        views.delete_competence,
        name="delete_competence",
    ),
]
