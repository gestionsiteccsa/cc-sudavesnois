from django.apps import AppConfig
from watson import search as watson


class PartenairesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "partenaires"

    def ready(self):
        from .models import Partenaire
        watson.register(Partenaire, fields=("nom", "description"))
