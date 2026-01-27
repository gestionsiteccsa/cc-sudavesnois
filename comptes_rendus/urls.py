from django.urls import path

from . import views

app_name = "comptes_rendus"

urlpatterns = [
    # Page publique
    path(
        "actes-administratifs/",
        views.comptes_rendus,
        name="comptes_rendus",
    ),
    path(
        "proces-verbaux-conseils-communautaires/",
        views.proces_verbaux,
        name="proces_verbaux",
    ),
    # Page admin
    path("adminccsa/cr-admin/", views.admin_page, name="admin_cr_list"),
    path("adminccsa/ajouter-conseil/", views.add_conseil, name="add_conseil"),
    path(
        "adminccsa/modifier-conseil/<int:conseil_id>/",
        views.edit_conseil,
        name="edit_conseil",
    ),
    path(
        "adminccsa/supprimer-conseil/<int:conseil_id>/",
        views.delete_conseil,
        name="delete_conseil",
    ),
    path("adminccsa/ajouter-cr-link/", views.add_cr_link, name="add_cr_link"),
    path(
        "adminccsa/modifier-cr-link/<int:cr_id>/",
        views.edit_cr_link,
        name="edit_cr_link",
    ),
    path(
        "adminccsa/supprimer-cr-link/<int:cr_id>/",
        views.delete_cr_link,
        name="delete_cr_link",
    ),
]
