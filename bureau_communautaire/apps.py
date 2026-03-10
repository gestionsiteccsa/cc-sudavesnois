from django.apps import AppConfig
from watson import search as watson


class BureauCommunautaireConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bureau_communautaire"

    def ready(self):
        from .models import Elus
        from django.urls import reverse
        
        class ElusAdapter(watson.SearchAdapter):
            def get_url(self, obj):
                return reverse('bureau-communautaire:elus')
        
        watson.register(Elus, ElusAdapter, fields=("first_name", "last_name", "function"))
