from django.urls import path

from . import views

app_name = "conseil_communautaire"

urlpatterns = [
    # Page d'accueil
    path("conseil-communautaire/", views.conseil, name="conseil"),
    # URL Ville
    path("adminccsa/ajouter-ville/", views.add_city, name="admin_add_city"),
    path("adminccsa/liste-ville/", views.list_cities, name="admin_list_cities"),
    path(
        "adminccsa/supprimer-ville/<int:city_id>/",
        views.delete_city,
        name="admin_delete_city",
    ),
    path(
        "adminccsa/modifier-ville/<int:city_id>/",
        views.edit_city,
        name="admin_edit_city",
    ),
    # URL Membres
    path("adminccsa/ajouter-membre/", views.add_member, name="admin_member_add"),
    path(
        "adminccsa/liste-membres/", views.admin_list_members, name="admin_membres_list"
    ),
    path(
        "adminccsa/modifier-membre/<int:id>/",
        views.edit_member,
        name="admin_member_edit",
    ),
    path(
        "adminccsa/supprimer-membre/<int:id>/",
        views.delete_member,
        name="admin_member_delete",
    ),
]
