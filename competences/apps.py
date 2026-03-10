from django.apps import AppConfig
from watson import search as watson


class CompetencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "competences"

    def ready(self):
        from .models import Competence
        watson.register(Competence, fields=("title", "description"))
