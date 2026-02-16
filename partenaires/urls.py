from django.urls import path
from . import views

app_name = "partenaires"

urlpatterns = [
    # Vue publique
    path("", views.partenaires, name="partenaires"),

    # URLs Admin - Catégories
    path("adminccsa/liste-categories/", views.list_categories, name="admin_categories_list"),
    path("adminccsa/ajouter-categorie/", views.add_categorie, name="add_categorie"),
    path("adminccsa/modifier-categorie/<int:id>/", views.edit_categorie, name="edit_categorie"),
    path("adminccsa/supprimer-categorie/<int:id>/", views.delete_categorie, name="delete_categorie"),

    # URLs Admin - Partenaires
    path("adminccsa/liste-partenaires/", views.list_partenaires, name="admin_partenaires_list"),
    path("adminccsa/ajouter-partenaire/", views.add_partenaire, name="add_partenaire"),
    path("adminccsa/modifier-partenaire/<int:id>/", views.edit_partenaire, name="edit_partenaire"),
    path("adminccsa/supprimer-partenaire/<int:id>/", views.delete_partenaire, name="delete_partenaire"),
]
