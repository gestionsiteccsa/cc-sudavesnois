from django.apps import AppConfig
from watson import search as watson


class ConseilCommunautaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "conseil_communautaire"
    
    def ready(self):
        from .models import ConseilVille
        from django.urls import reverse
        
        class ConseilVilleAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('conseil_communautaire:conseil')
        
        watson.register(ConseilVille, ConseilVilleAdapter, fields=("city_name", "slogan"))
