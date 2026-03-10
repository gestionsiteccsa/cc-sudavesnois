from django.apps import AppConfig
from watson import search as watson


class JournalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "journal"
    
    def ready(self):
        from .models import Journal
        from django.urls import reverse
        
        class JournalAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('journal:journal')
        
        watson.register(Journal, JournalAdapter, fields=("title",))
