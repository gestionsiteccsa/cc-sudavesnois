from django.apps import AppConfig
from watson import search as watson


class ComptesRendusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "comptes_rendus"

    def ready(self):
        from .models import Conseil
        watson.register(Conseil, fields=("place",))
