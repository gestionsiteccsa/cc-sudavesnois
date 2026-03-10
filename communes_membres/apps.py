from django.apps import AppConfig
from watson import search as watson


class CommunesMembresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communes_membres"
    
    def ready(self):
        from .models import ActeLocal
        watson.register(ActeLocal, fields=("title", "description"))
