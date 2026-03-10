from django.apps import AppConfig
from watson import search as watson


class RapportsActiviteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rapports_activite"

    def ready(self):
        from .models import RapportActivite
        watson.register(RapportActivite, fields=("title", "description"))
