from django.urls import path

from . import views

app_name = "communes-membres"


urlpatterns = [
    # Pages publiques
    path("<slug:slug>/", views.commune, name="commune"),
    # Pages d'administration
    path("adminccsa/ajouter-acte/", views.add_acte_local, name="admin_acte_add"),
    path("adminccsa/liste-actes/", views.list_acte_local, name="admin_acte_list"),
    path(
        "adminccsa/modifier-acte/<int:id>/",
        views.update_acte_local,
        name="admin_acte_update",
    ),
    path(
        "adminccsa/supprimer-acte/<int:id>/",
        views.delete_acte_local,
        name="admin_acte_delete",
    ),
]
