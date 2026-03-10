from django.apps import AppConfig
from watson import search as watson


class CompetencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "competences"

    def ready(self):
        from .models import Competence
        from django.urls import reverse
        
        class CompetenceAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('competences:competences')
        
        watson.register(Competence, CompetenceAdapter, fields=("title", "description"))
