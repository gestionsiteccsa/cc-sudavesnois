from django.urls import path

from . import views

app_name = "semestriels"

urlpatterns = [
    # Calendrier semestriel des manifestations
    path("semestriels/", views.semestriel, name="semestriel"),
    # Page d'administration
    path("adminccsa/semestriels/ajouter/", views.add_content, name="add_content"),
    path(
        "adminccsa/semestriels/modifier/<int:pk>/",
        views.edit_content,
        name="edit_content",
    ),
    path(
        "adminccsa/semestriels/liste-evenements/",
        views.list_content,
        name="list_content",
    ),
]
