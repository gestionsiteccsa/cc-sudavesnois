from django.apps import AppConfig
from watson import search as watson


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"
    
    def ready(self):
        from .models import Service
        watson.register(Service, fields=("title", "content"), store=("icon",))
