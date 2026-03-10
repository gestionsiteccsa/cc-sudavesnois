from django.apps import AppConfig
from watson import search as watson


class PartenairesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "partenaires"

    def ready(self):
        from .models import Partenaire
        from django.urls import reverse
        
        class PartenaireAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('partenaires:partenaires')
        
        watson.register(Partenaire, PartenaireAdapter, fields=("nom", "description"))
