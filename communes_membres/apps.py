from django.apps import AppConfig
from watson import search as watson


class CommunesMembresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "communes_membres"
    
    def ready(self):
        from .models import ActeLocal
        from django.urls import reverse
        
        class ActeLocalAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                # Redirige vers la page de la commune concernée
                return reverse('communes-membres:commune', kwargs={'slug': obj.commune.slug})
        
        watson.register(ActeLocal, ActeLocalAdapter, fields=("title", "description"))
