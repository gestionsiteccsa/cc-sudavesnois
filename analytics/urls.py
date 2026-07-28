from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("adminccsa/statistiques/", views.admin_stats, name="admin_stats"),
    path("adminccsa/statistiques/live/", views.live_stats, name="live_stats"),
    path(
        "adminccsa/statistiques/telecharger/tout/",
        views.download_all_json,
        name="download_all",
    ),
    path(
        "adminccsa/statistiques/telecharger/<str:day_str>/",
        views.download_day_json,
        name="download_day",
    ),
    path(
        "adminccsa/statistiques/supprimer/<str:day_str>/",
        views.delete_day_stats,
        name="delete_day",
    ),
    path(
        "adminccsa/statistiques/supprimer-lot/",
        views.batch_delete,
        name="batch_delete",
    ),
    path(
        "adminccsa/statistiques/telecharger-lot/",
        views.batch_export,
        name="batch_export",
    ),
    path(
        "adminccsa/statistiques/export-pdf/",
        views.export_pdf,
        name="export_pdf",
    ),
    path(
        "adminccsa/statistiques/envoyer-rapport/",
        views.send_email_report,
        name="send_email_report",
    ),
    path("adminccsa/changelog/", views.admin_changelog, name="admin_changelog"),
]
