from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    path("adminccsa/liste-contacts/", views.list_contact_emails, name="list_contacts"),
    path(
        "adminccsa/modifier-contact/<int:id>/",
        views.edit_contact_email,
        name="edit_contact",
    ),
    path(
        "adminccsa/supprimer-contact/<int:id>/",
        views.delete_contact_email,
        name="delete_contact",
    ),
    path("adminccsa/ajouter-contact/", views.add_contact_email, name="add_contact"),
]
