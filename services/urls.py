from django.urls import path

from . import views

app_name = "services"
urlpatterns = [
    # Page d'ajout d'un service
    path("adminccsa/ajout-service/", views.add_service, name="add_service"),
    # Page de modification d'un service
    path(
        "adminccsa/modifier-service/<int:id>",
        views.update_service,
        name="update_service",
    ),
    # Page de suppression d'un service
    path(
        "adminccsa/supprimer-service/<int:id>",
        views.delete_service,
        name="delete_service",
    ),
    # Page de liste des services
    path("adminccsa/liste-services/", views.service_list, name="admin_services_list"),
]
