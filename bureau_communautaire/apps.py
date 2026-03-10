from django.apps import AppConfig
from watson import search as watson


class BureauCommunautaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bureau_communautaire"

    def ready(self):
        from .models import Elus
        watson.register(Elus, fields=("first_name", "last_name", "function"))
