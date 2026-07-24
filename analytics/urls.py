from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("adminccsa/statistiques/", views.admin_stats, name="admin_stats"),
    path(
        "adminccsa/statistiques/telecharger/<str:day_str>/",
        views.download_day_json,
        name="download_day",
    ),
    path(
        "adminccsa/statistiques/telecharger/tout/",
        views.download_all_json,
        name="download_all",
    ),
]
