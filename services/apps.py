from django.apps import AppConfig
from watson import search as watson


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"
    
    def ready(self):
        from .models import Service
        from django.urls import reverse
        
        class ServiceAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                # Les services sont sur la page d'accueil
                return reverse('home')
        
        watson.register(Service, ServiceAdapter, fields=("title", "content"))
