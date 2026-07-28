from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analytics"
    verbose_name = "Statistiques de visites"

    def ready(self):
        from analytics.analytics_data import ensure_dir

        ensure_dir()
