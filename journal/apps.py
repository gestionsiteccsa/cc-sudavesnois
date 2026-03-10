from django.apps import AppConfig
from watson import search as watson


class JournalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "journal"
    
    def ready(self):
        from .models import Journal
        watson.register(Journal, fields=("title",), store=("number",))
