from django.urls import path

from . import views

app_name = "journal"  # Ajout du namespace

urlpatterns = [
    path("journal/", views.journal, name="journal"),
    path("journal/<int:id>/", views.journal_detail, name="journal_detail"),
    # Administration des journaux
    path("adminccsa/ajouter-journal/", views.add_journal, name="add_journal"),
    path("adminccsa/liste-journaux/", views.list_journals, name="admin_journaux_list"),
    path(
        "adminccsa/supprimer-journal/<int:id>/",
        views.delete_journal,
        name="delete_journal",
    ),
    path(
        "adminccsa/modifier-journal/<int:id>/", views.edit_journal, name="edit_journal"
    ),
]
