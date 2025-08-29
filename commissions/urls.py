from django.urls import path

from . import views

app_name = "commissions"  # Ajout du namespace

urlpatterns = [
    # URL de la page des commissions
    path("commissions/", views.commissions, name="commissions"),
    # URLs d'administration des commissions
    # Partie commissions
    path("adminccsa/ajouter/", views.add_commission, name="admin_add_commission"),
    path("adminccsa/liste/", views.list_commission, name="admin_list_commissions"),
    path(
        "adminccsa/modifier/<int:commission_id>/",
        views.edit_commission,
        name="admin_edit_commission",
    ),
    path(
        "adminccsa/supprimer/<int:commission_id>/",
        views.delete_commission,
        name="admin_delete_commission",
    ),
    # Partie documents
    path(
        "adminccsa/commission/upload/", views.add_document, name="upload_commission_doc"
    ),
    path(
        "adminccsa/commission/modifier_doc/<int:document_id>/",
        views.edit_document,
        name="edit_document",
    ),
    path(
        "adminccsa/commission/supprimer_doc/<int:document_id>/",
        views.delete_document,
        name="delete_document",
    ),
    # Partie mandats
    path(
        "adminccsa/mandat/modifier/<int:mandat_id>/",
        views.edit_mandat,
        name="edit_mandat",
    ),
]
