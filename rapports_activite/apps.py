from django.apps import AppConfig
from watson import search as watson


class RapportsActiviteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rapports_activite"

    def ready(self):
        from .models import RapportActivite
        from django.urls import reverse
        
        class RapportAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('rapports_activite:rapports_activite')
        
        watson.register(RapportActivite, RapportAdapter, fields=("title", "description"))
