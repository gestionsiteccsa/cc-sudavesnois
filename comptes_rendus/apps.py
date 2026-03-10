from django.apps import AppConfig
from watson import search as watson


class ComptesRendusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "comptes_rendus"
    
    def ready(self):
        from .models import Conseil
        from django.urls import reverse
        
        class ConseilAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('comptes_rendus:comptes_rendus')
        
        watson.register(Conseil, ConseilAdapter, fields=("place",))
