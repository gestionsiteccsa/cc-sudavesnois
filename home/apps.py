from django.apps import AppConfig
from watson import search as watson


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"
    
    def ready(self):
        from .models import StaticPage
        watson.register(StaticPage, fields=("title", "content", "description"), store=("url",))
