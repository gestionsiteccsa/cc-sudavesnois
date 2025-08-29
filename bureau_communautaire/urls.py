from django.urls import path

from . import views

app_name = "bureau-communautaire"


urlpatterns = [
    # Pages publiques
    path("bureau-communautaire/", views.elus, name="elus"),
    # Pages d'administration
    path("adminccsa/ajouter-elu/", views.add_elu, name="admin_elu_add"),
    path("adminccsa/liste-elus/", views.list_elus, name="admin_elus_list"),
    path("adminccsa/modifier-elu/<int:id>/", views.update_elu, name="admin_elu_update"),
    path(
        "adminccsa/supprimer-elu/<int:id>/", views.delete_elu, name="admin_elu_delete"
    ),
    path("adminccsa/ajouter-document/", views.add_document, name="admin_document_add"),
    path(
        "adminccsa/liste-documents/", views.list_documents, name="admin_documents_list"
    ),
    path(
        "adminccsa/modifier-document/<int:id>/",
        views.update_document,
        name="admin_document_update",
    ),
    path(
        "adminccsa/supprimer-document/<int:id>/",
        views.delete_document,
        name="admin_document_delete",
    ),
]
