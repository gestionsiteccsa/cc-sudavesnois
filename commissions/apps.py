from django.apps import AppConfig
from watson import search as watson


class CommissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "commissions"

    def ready(self):
        from .models import Commission
        watson.register(Commission, fields=("title",))
