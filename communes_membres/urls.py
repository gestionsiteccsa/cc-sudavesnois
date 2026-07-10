from django.urls import path

from . import views

app_name = "communes-membres"


urlpatterns = [
    # Pages publiques
    # Note : le pattern de liste est déclaré AVANT le pattern <slug:slug>/
    # pour éviter qu'un slug "communes-membres" ne capture l'URL de listing.
    path("communes-membres/", views.communes_list, name="list"),
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
